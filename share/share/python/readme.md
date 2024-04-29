# python classes and demos


## content

* **multiDaq.py**  
This is the base interface for measurements.  
contains a high level class and a low level class.  
The low level class is accessible for high level class.  

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
```
pip install numpy
pip install matplotlib
```
Hopefully thats it.

## run

**Windows**


You need biovisionMultiDaq.dll in Path or in your working directory.


**Linux**

drivers must be installed. Run install.sh in the root folder, if not done yet.


 