import json
import os


def load_json(in_file):
    with open(in_file, 'r') as fin:
        return_dict = json.load(fin)
    return return_dict


# def main():
#     data_folder = '/remote-home/pli/mango/data'
#     game_name_list = sorted(os.listdir(data_folder))
#     sum_all2all = 0
#     sum_allpairs = 0
#     for idx, game_name in enumerate(game_name_list):
#         all2all_path = '{}/{}/{}.all2all.json'.format(data_folder, game_name, game_name)
#         allpairs_path = '{}/{}/{}.all_pairs.json'.format(data_folder, game_name, game_name)

#         all2all_num = len(load_json(all2all_path))
#         allpairs_num = len(load_json(allpairs_path))
#         print ("{}\t{}\t{}\t{}".format(idx,game_name,all2all_num,allpairs_num))
#         sum_all2all += all2all_num
#         sum_allpairs += allpairs_num
    
#     print ("all2all sum: ", sum_all2all)
#     print ("allpairs sum: ", sum_allpairs)


import os

def count_files_in_subdirectories(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            directory_path = os.path.join(root, directory)
            file_count = len(os.listdir(directory_path))
            print(f"# directory_path {directory_path}：{file_count}")


folder_path = "/remote-home/pli/mango/inhouse_llms_results_pli"

count_files_in_subdirectories(folder_path)



# if __name__ == '__main__':
#     main()