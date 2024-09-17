import splitfolders


input_path = 'dataset/test'
output_path = 'dataset/split_test_val'

#Split folders with files (e.g. images) into train, validation and test (dataset) folders
splitfolders.ratio(
    input=input_path, 
    output=output_path,
    seed=42, 
    ratio=(0.5,0.5), 
    group_prefix=None, 
    move=False) 