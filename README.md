dogtag
======

Some utilities to 3D print dogtag-style name badges.

To install, clone the repo and create a virtualenv in it:

```
git clone https://github.com/Eigenbaukombinat/dogtag.git
cd dogtag
python3 -m venv .
bin/pip install -r requirements.txt
```

To create a tag, call the make_name script, with the text as the parameter:

```
./make_name this is my tag
```

This will result in two files: out.stl and out.png

