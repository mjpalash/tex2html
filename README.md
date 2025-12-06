# Project Title

# What is it?
Use tex2html to go from your tex files to a publish into a github site. 

# What does it do? 
It converts your latex project into an html file that can be published as an article on a website. It uses Pandoc to convert tex file(s) into html. 

# How does it do it?

A workflow program reads the config file (to know Github pages location and whether to push changes to github pages to remote), creates an html out of the tex file, regenerates the index file for Github pages (so that it can have a link to the newly created article), and pushes all the changes in the Github pages site to remote. 

Here are the files in the repo:
1. setup: Creates a settings file that tells where the Sites repo is. 
2. convert: Runs pandoc with appropriate params and copies the generated html (and images) to the sites folder and creates a new folder with all this content. 
3. buildindex: Updates the index file to create a list of such folders (each of which correspond to an article converted from tex) so that reader can conveniently see the list and click on the one they want to read. 
4. gitpush: If the settings allow it, this pushes all the changes to github. 

All these are python files, so you need to do python3 <script name> to run. 


## Getting Started
Before you start, make sure you have a clone of your Github sites repo. Let's say we call it latex-web. 

To convert your tex file to html and push into your Github pages, execute the following on your terminal. 

```
python3 workflow.py
```

The instructions from the script will guide you. It will ask you the path to the latex-web folder, and whether latex-web should be committed and pushed automatically after changes. 


### Prerequisites

This script has been tested only on Mac. You need to have Python 3 installed on your machine. 

### Installing


Clone or download the zip and run 
```
python3 workflow.py
```



## Built With

* [Pandoc](https://pandoc.org/) - Tex to html converter

## Contributing
Please review [CONTRIBUTING.md](CONTRIBUTING.md)


## Authors
**Mrityunjay Kumar** - *Initial work* 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* OSSE course students at BITS Pilani WILP program
