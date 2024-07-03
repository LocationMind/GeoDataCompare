# Useful commands

- [Useful commands](#useful-commands)
  - [Create virtual environnment](#create-virtual-environnment)
  - [Ugrade pip](#ugrade-pip)
  - [Install dependencies](#install-dependencies)
  - [Push to a new branch on github](#push-to-a-new-branch-on-github)
  - [Install act (tool to run github actions locally)](#install-act-tool-to-run-github-actions-locally)
  - [Path of python in windows](#path-of-python-in-windows)


## Create virtual environnment

**Delete directory**

```console
rmdir /S /Q .venv 
```

**Create and activate virtual environment**

```console
python -m venv .venv
.venv\Scripts\activate
```

To activate the virtual environnment: 

```console
.venv\Scripts\activate
```

To deactivate it:

```console
.venv\Scripts\deactivate.bat
```

## Ugrade pip

```console
python.exe -m pip install --upgrade pip
```

## Install dependencies

```console
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

## Push to a new branch on github

```console
git branch <mybranch>
git push -u origin <mybranch>
```

If there is an error, try
```
git push --set-upstream origin tests_functions
```

## Install act (tool to run github actions locally)

Following this document : https://gist.github.com/sweetlilmre/758818d0b2a0fdfd79595e396d1e608d.

**Install scoop**

In a powershell command

```console
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

**Install act**
```console
scoop bucket add main
scoop install main/act
```

**Install docker**

On this website : https://www.docker.com/products/docker-desktop/

Download the installer and follow the procedure

**Install wls**

```console
wsl --install
```

Then type your username and password (mathis for both).

## Path of python in windows

C:\Users\Mathis.Rouillard\AppData\Local\Programs\Python\Python312\Scripts\
C:\Users\Mathis.Rouillard\AppData\Local\Programs\Python\Python312\
C:\Users\Mathis.Rouillard\AppData\Local\Programs\Python\Python310\Scripts\
C:\Users\Mathis.Rouillard\AppData\Local\Programs\Python\Python310\