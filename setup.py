from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sify-ai-platform",
    version="0.0.1",
    author="InfinitAIML",
    description="A package for Sify's AI Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sifymdp/sify-ai-platform",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests"
    ],
    extras_require={
        "data": ["pandas","numpy"],
        "viz": ["matplotlib","seaborn","wordcloud","plotly"],
        "ml": ["bertopic","scikit-learn","hdbscan","umap-learn"],
        "nlp": ["nltk", "spacy", "transformers", "sentence-transformers"],
    },
)