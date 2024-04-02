# Data

## Data location

Our data are hosted on Huggingface.
We provide access to the following collections:

| Name | Description | Purpose |
| --------------- | ----------- | ------- |
| [data/huggingface](https://huggingface.co/datasets/mango-ttic/data) | A cleaned collection that only contains test-ready releases | Good for LLM benchmark |
| [data-intermediate/huggingface](https://huggingface.co/datasets/mango-ttic/data-intermediate) | A full collection with all of our labeling and intermediate files | If you are interested in dig deeper into data labeling, or derive further customized version |


## Word-only vs Word+ID

**word-only**: We have one version where all nodes are labeled by additional descriptive text to distinguish different locations with similar names.

**word+ID**: In addition, we also prepared another version, where nodes are labeled using minimaly fixed Jericho simulator names with randomized id.

We primarily rely on the word-only version as benchmark, yet providing word+ID version for diverse benchmark settings.
