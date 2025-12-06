# What is it?
Use texpub to go from your tex files to a publish into a github site. 

# What does it do? 
It takes your tex file(s) and use pandoc to convert them into html. Then it copies those files and corresponding images into a github sites folder of your choosing and optionally pushes the changes so that the site gets updated. 

# How does it do it?
1. setup (Script A): Creates a settings file that tells where the Sites repo is. 
2. convert (Script B): Runs pandoc with appropriate params and copies the generated html (and images) to the sites folder and creates a new folder with all this content. 
3. buildindex (Script C): Updates the index file to create a list of such folders (each of which correspond to an article converted from tex) so that reader can conveniently see the list and click on the one they want to read. 
4. gitpush (Script D): If the settings allow it, this pushes all the changes to github. 

All these are python files, so you need to do python3 <script name> to run. 

