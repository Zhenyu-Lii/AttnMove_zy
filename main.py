import os
#要加载的CDR文件数目
fileNumbers = 1

def mode_gen_raw_data():
    for fileNumbers in [1,2,5,10]:
        os.system('python ./genRawData.py --fileNumbers %d' % (fileNumbers))

def mode_test_work_flow():
    for fileNumbers in [1,2,5,10]:
        os.system('python ./dropNaN.py --fileNumbers %d' % (fileNumbers))
        os.system('python ./convertFormat.py --fileNumbers %d' % (fileNumbers))

def mode_gen_final_data():
    fileNumbers = 50
    os.system('python ./genRawData.py --fileNumbers %d' % (fileNumbers))
    os.system('python ./dropNaN.py --fileNumbers %d' % (fileNumbers))
    os.system('python ./convertFormat.py --fileNumbers %d' % (fileNumbers))

if __name__ == "__main__":
    # mode_gen_raw_data()
    #mode_test_work_flow()
    mode_gen_final_data()
