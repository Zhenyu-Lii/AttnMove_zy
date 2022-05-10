import pandas as pd
from datetime import datetime
import os
import argparse

def _main(end):
    output_path = './Results/size%d' % (end)
    if not os.path.exists(output_path):
        # 目录不存在，进行创建操作
        os.makedirs(output_path)

    startTime = datetime.now()
    traj_undropped = pd.read_csv(output_path + '/raw_pos.txt',sep="\t")
    traj_undropped.index = list(traj_undropped.iloc[:,0])
    # 删除采样点少于12个的轨迹
    i = 0
    traj_dropped = pd.DataFrame()
    while i<len(traj_undropped):
        count = traj_undropped.iloc[i].value_counts()['*']
        print("Trajectory %d has %d missing values."%(i+1,count))
        if count<36:
            traj_dropped = traj_dropped.append(traj_undropped.iloc[i])
        i += 1

    # 删除轨迹少于5条的用户
    traj_drop_uid = pd.DataFrame()
    date_counts = traj_dropped.index.value_counts()
    for uid in date_counts.index:
        if date_counts[uid]>1:
            traj_drop_uid = traj_drop_uid.append(traj_dropped.loc[uid])
    endTime = datetime.now()
    print("Dropping time:",str(endTime-startTime)[0:7])

    #删除小数点
    traj_drop_uid.replace('*',0,inplace=True)
    traj_drop_uid = traj_drop_uid.astype(float)
    traj_drop_uid = traj_drop_uid.astype(int)
    traj_drop_uid.replace(0,'*',inplace=True)

    #给用户重新编号
    keys = set(traj_drop_uid.index)
    values = [i for i in range(1, len(keys) + 1)]
    tmp_dict = dict(zip(keys, values))
    traj_drop_uid['Unnamed: 0'] = traj_drop_uid.apply(lambda x:tmp_dict[x["Unnamed: 0"]], axis=1)
    traj_drop_uid.sort_values(by="Unnamed: 0" , inplace=True, ascending=True)

    endTime = datetime.now()
    print("Total time:",str(endTime-startTime)[0:7])

    print("generate dropped_pos.txt...")
    traj_drop_uid.to_csv(output_path + '/dropped_pos.txt',sep='\t',index=False,header=1)
    print("generatation completed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--fileNumbers", type=int, default=10)
    args = parser.parse_args()
    print("execute dropNAN.py")
    _main(args.fileNumbers)