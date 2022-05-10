import pandas as pd
import os
import time
from datetime import datetime
import argparse


# 根据经纬度映射出区域号
def get_regionID(longitude, latitude):
    xlim = [111.55, 113.37]
    ylim = [35.12, 36.3]
    grid_length = 0.001
    grid_width = 0.001
    regionID = (xlim[1] - xlim[0]) // grid_length * (latitude - ylim[0]) // grid_width + (
            longitude - xlim[0]) // grid_length + 1
    return int(regionID)


def _main(end):
    file_list = sorted(os.listdir('./data'))
    output_path = './Results/size%d' % (end)
    if not os.path.exists(output_path):
        # 目录不存在，进行创建操作
        os.makedirs(output_path)

    # 读取CDR数据集前end项
    time0 = datetime.now()
    start_time = datetime.now()
    result_tmp = []
    data_tmp = pd.DataFrame()
    data_all = pd.DataFrame()
    # data_all.columns=['UID','timestamp','longitude','latitude']
    for filename in file_list[0:end]:
        f = open('./data/' + filename, 'r')
        for line in f.readlines():  # readlines以列表输出文件内容
            # line=line.strip().split(",")
            # result.append(line)
            line = line.strip().split(",")
            uid = line[0:1]
            others = list(map(lambda x: float(x), line[1:]))
            temp = uid + others
            result_tmp.append(temp)
        f.close()
        print(filename + 'is read.')
        data_all = pd.DataFrame(result_tmp, columns=['UID', 'timestamp', 'longitude', 'latitude']).dropna(axis=0)
        print("当前区域个数：", len(data_all.iloc[:, 2].value_counts()))
    end_time = datetime.now()
    print("Loading Time:", str((end_time - start_time))[0:7])

    start_time = datetime.now()
    tmp = data_all.copy(deep=True)
    # 经纬度
    tmp['longitude'] = tmp['longitude'] + 100
    tmp['latitude'] = tmp['latitude'] + 30
    # UID
    tmp['UID'] = tmp['UID'].apply(lambda x: int(x))
    # 获取日期
    tmp['date'] = tmp['timestamp'].apply(lambda x: int(time.strftime("%Y%m%d", time.localtime(x + 1633017600))))
    # 获取具体时间（24小时制）
    tmp['time'] = tmp['timestamp'].apply(lambda x: time.strftime("%H:%M:%S", time.localtime(x + 1633017600)))
    # 获取时间编号（48个半小时中的第几个）
    tmp['timeNo'] = tmp['time'].apply(lambda x: int(x[0:2]) * 2 + int(x[3:5]) // 30)
    # 获得区域编号
    tmp['regionID'] = tmp.apply(lambda x: get_regionID(x['longitude'], x['latitude']), axis=1)

    # 给区域重新编号
    print("reindex regionID...")
    keys = []
    keys += set(tmp['regionID'])
    keys = [i for n, i in enumerate(keys) if i not in keys[:n]]
    print("After loading the first %d data files，region numbers: " % (end), len(keys))
    values = [i for i in range(1, len(keys) + 1)]
    tmp_dict = dict(zip(keys, values))
    tmp['regionID'] = tmp.apply(lambda x: tmp_dict[x['regionID']], axis=1)
    end_time = datetime.now()
    print("Time for reindexing regionID:", str((end_time - start_time))[0:7])

    # 转换成AttnMove的数据格式：{uid, date, trajectory}
    start_time = datetime.now()
    print("generate raw_pos.csv...")
    tmp3 = tmp[['UID', 'date', 'regionID', 'timeNo']].copy(deep=True)
    tmp3['regionID'] = tmp3['regionID'].apply(lambda x: str(x))
    tmp3 = tmp3.groupby(['UID', 'date']).apply(lambda x: x[:])
    tmp3 = tmp3.drop_duplicates(subset=['UID', 'timeNo'])
    tmp3.to_csv('./Results/tmp3.txt', sep='\t', index=False)

    # 获得user_list和date_list
    tmp3 = pd.read_csv('Results/tmp3.txt', sep="\t").groupby(['UID', 'date']).apply(lambda x: x[:])
    user_list = tmp3['UID'].drop_duplicates().values
    date_list = tmp3['date'].drop_duplicates().values

    # result_final是符合AttnMove数据格式的dataframe
    result_final = pd.DataFrame()
    for uid in user_list:
        for date in date_list:
            try:
                tmp4 = pd.DataFrame(tmp3.loc[(uid, date), ['timeNo', 'regionID']].values.T)
                tmp4 = tmp4.set_axis(tmp4.iloc[0], axis=1, inplace=False).drop(index=0)
                tmp4.index = pd.MultiIndex.from_product([[uid], [date]])
                result_final = result_final.append(tmp4)
            except:
                print("No record for UID=%d, date=%d" % (uid, date))
                continue
    result_final = result_final.fillna('*')
    end_time = datetime.now()
    print("Time for converting format:", str((end_time - start_time))[0:7])
    time1 = datetime.now()
    print("Total time:", str(time1 - time0)[0:7])

    # 运行一次太慢了，因此跑完之后存下来方便之后直接用
    result_final.to_csv(output_path + '/raw_pos.csv', index=True, header=1)
    df_tmp = pd.read_csv(output_path + '/raw_pos.csv', index_col=0)
    df_tmp.to_csv(output_path + '/raw_pos.txt', sep='\t', index=True, header=1)


# result_final.to_csv('./Results/raw_pos.txt',sep='\t',index=True,header=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--fileNumbers", type=int, default=1)
    args = parser.parse_args()
    print("\nSize of dataset to load: ", args.fileNumbers)
    _main(args.fileNumbers)
