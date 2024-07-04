# python classes and demos


## content

* **multidaq**
folder with the modules for measurements.
it contains the module files (e.g. multidaq.py)

* **demo1.py**  
example, how to handle low level class ( multiDaqLowLevel() )

* **demo2.py**  
example, how to handle 2 devices simultanously with low level class

* **demoHighLevel.py**
example, how to handle high level class

* **demoTrigger.py**
example, how to use the Trigger Interface  
uses both, high level and low level interface

* **demoGraph.py**
example, how to use the build in Graphic Window.  
shows monitoring Graphic window during a measurement


## prerequisites

* You need numpy  
* for demoHighLevel.py matplotlib too

Install in terminal:
```bash
pip install numpy
pip install matplotlib
```

**Linux**

SDL must be installed, because drivers depend on it.
install.sh in the root folder will do that job.
If you do not want to install the drivers with install.sh, open a command terminal:

```bash
sudo apt-get install libsdl2-2.0-0 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0
```


## run

needed DLLs are integrated in the module now, so nothing is to install.


We also offer our modules on PyPI. You may install multidaq with pip in a normal way.
('pip install multidaq') Then the folder multidaq in share/python/ can be deleted.
It is not needed any more.

If you do that way, the via pip installed module will be used automaticly instead.

 