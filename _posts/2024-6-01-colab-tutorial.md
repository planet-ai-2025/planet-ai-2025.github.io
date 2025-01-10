---
layout: post
title:  "Colab Tutorial"
date: 2024-06-01
image: assets/images/colab_favicon_256px.png
tags: [ AI, tutorials, resources, summer2024 ]
---

Google Colab is a free Jupyter notebook environment that runs in the cloud. You can use Google Colab from your browser so you don't have to install anything on your own computer. With Google Colab, you can access Google's computing resources, write and execture code, save and share.   

**1. Login your Gmail account**   
&nbsp;   
**2. Go to the url link:** 
[https://colab.research.google.com/](https://colab.research.google.com/){:target="_blank"}

**3. Top pane**  
&nbsp;    
<img width=900 src="/assets/images/top_pane_colab.png" class="img-fluid" />
&nbsp; 

- Top menu: You can see the Colab logo from the top left, and then you can find the top menu, including File, Edit, View, Insert, Runtime, etc.   
- <code>Share</code>: On the top right, the <code>Share</code> button gives you the option of creating a shareable link that you can share with others. 
- <code>+ Code</code>: Under the top menu, the <code>+ Code</code> will let you add more code cells.
- <code>+ Text</code>: will let you add more text cells. 
- <code>Copy to Drive</code>: allows you to copy this Colab notebook into your Colabe Notebook directory in your Google Drive.
- <code>Connect</code>: will let you connet this Colab notebook to the runtime.  

**4. Left pane**
&nbsp;    
<img width=30 src="/assets/images/left_pane_1.png" class="img-fluid" />
&nbsp;  

Click <code>Files</code>, and it will expand the left pane.  

&nbsp;    
<img width=400 src="/assets/images/left_pane_2.png" class="img-fluid" />
&nbsp;

Then you can browse the directory structure on the left file-exlorer pane. 
- Upload: You can right click (your mouse) and choose <code>Upload</code> in order to upload files to the Colab. Since Colab notebook is hosted on Google's cloud servers, there's no direct access to files on your local computer. Or you can click the three dots visible when your mouse hovers above the directory and then you can select the "Upload" option.
- Download: Hover your mouse above the filename you want to download, and you will see three dots. Click on the three dots and select the <code>Download</code> option.

**5. Mount your Google Drive to Colab**   
- Executing the following code to mount your Google Drive to Colab, and click "agree".   
<code>from google.colab import drive</code>   
<code>drive.mount('/content/gdrive')</code>

**6. Use the Bash Commands**   
- You can use most of the bash commands with a <code>!</code> added in front of the command.  
- You can also use magic commands with <code>%</code>.   
- Use <code>%</code> instead of <code>!</code> for cd (change directory) command

**7. Use GPUs on Colab**   
- If you use the free GPU, click and choose <code>Runtime</code> -> <code>Change Runtime Type</code> -> <code>Hardware accelerator</code>   
- If you use the paid version of the GPUs, click and choose <code>Runtime</code> -> <code>Change Runtime Type</code>, then you will choose the following:
<img width=350 src="/assets/images/gpu_colab.png" class="img-fluid" alt="Colab GPUs" />   
Click <code>Save</code>.
<br/>
<br/>

- Check GPUs   

<img width=700 src="/assets/images/check_gpu.png" class="img-fluid" alt="GPUs" />
<br/>
<br/>


<br/>
<br/>
<br/>
<br/>


