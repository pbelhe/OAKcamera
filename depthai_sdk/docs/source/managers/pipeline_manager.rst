================
Pipeline manager
================

:obj:`PipelineManager` is the first class that we will learn how to use as it is the one that is goes hand in hand with every other class.
It is created with the purpose to help you with creating and setting up processing pipelines. In this tutorial bellow we will see and learn how to declare and use them.


Getting started
---------------

Before we begin we must first import ``pipeline_manager`` from ``DepthAI_SDK``. After that we will initialize the pipeline and define its sources.

.. literalinclude:: ../examples/code_fractions/pipeline.py
   :language: python
   :linenos:

We successfully created and initialized the pipeline. If everything was setup correctly, you should receive a message in your terminal, that will inform you that the connecting was successful.

.. image:: /_static/images/connecting_message.png

But the above code currently one has one source as it's stream. We can initialize more sources in one pipeline.

.. literalinclude:: ../examples/code_fractions/pipeline_more.py
   :language: python
   :linenos:

We now declared more then one source in the pipeline. To fully use the pipeline, you can use it with :obj:`PreviewManager` to see the streams or :obj:`EncodingManager` to save streams to files.
As you can see above we also added another argument to the color camera stream, called ``previewSize`` which will resize the stream to wanted ratio (height x width). All sources have many more arguments,
``xout`` will help us in the next tutorial where we will learn about the :obj:`PreviewManager`.
In the above example we also declared a ``Depth`` source. We gave it ``useDepth`` as an argument which will create a queue for depth frames. If we wish to use a different queue for depth,
we can change this argument to:
- ``useDisparity`` to use disparity frames,
- ``useRectifiedLeft`` for rectified left frames,
- and ``useRectifiedRigh`` for rectified right frames.
Of course these are not the only arguments that you can use in the :obj:`PipelineManager`.
To see all functions and arguments that the manager can contain check :ref:`DepthAI SDK API`.

.. include::  footer-short.rst