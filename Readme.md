#Brainforge documentation
Brainforge is an Artificial Neural Networking library implemented in Python,
which only depends on NumPy.

The interface is intended to look like Keras' interface, but no compilation
is done in the background.

##Layers
Neural networking operations are implemented as Layer subclasses and an
ANN can be thought of a stack of Layer instances.

###Core layers
These layers are the ones used most regularily when working with ANNs.

- InputLayer: passes the input tensor forward, unmodified.
- Flatten: performs flattening on a *dims* dimensional tensor. Returns a matrix of shape
(*batch_size*, prod(*dims*))
- Reshape: reshapes the input tensor to a given shape. Keeps the leading dimension,
which corresponds to *batch_size*
- DenseLayer: just your regular densely connected layer.
- Activation: applies a (possibly) nonlinear activation function elementwise on the
input tensor. Currently available activation funcions:
**sigmoid, tanh, relu, softmax**

###Fancy layers
Some fancy feedforward layers from various scientific articles

- HighwayLayer: used in the constriction of a Highway Network, see Srivastava et al., 2015
- DropOut: performs dropout with given dropchance (p). See Srivastava et al., 2014

###Recurrent
Recurrent layersworking with multidimensional (time-series) data

- RLayer: simple recurrence, output is simply fed back in each timestep.
- LSTM: Long-Short Term Memory, see Hochreiter et al., 1997
- EchoLayer: an untrainable, specially initialized recurrent layer used
in Echo State Network. See Reservoir computing and Jaeger, 2007 (Scholarpaedia)

###Tensor
Feedforward layers working with multidimensional data

- PoolLayer: untrainable layer performing the max-pooling operation
- ConvLayer: performs convolution on a batch of images by learnable kernels
of a given shape.

##Evolution
Experimental support is available for the optimization of hyperparameters
using a simple genetic algorithm.

##Exaplmes
###Simple shallow Dense network
```python
import numpy as np

from brainforge import Network
from brainforge.layers import DenseLayer

X = np.random.randn(120, 30)
Y = np.zeros(120, 3).astype(float)
Y[:40, 0] += 1.
Y[40:80, 1] += 1.
Y[80:, 2] += 1.

brain = Network(input_shape=X.shape[1:], layers=(
    DenseLayer(10, activation="tanh"),
    DenseLayer(Y.shape[1:], activation="sigmoid")
))
brain.finalize(cost="xent", optimizer="adam")
brain.fit(X, Y, verbose=1)
```
For more complicated tasks, the use of the library csxdata is suggested.
###Fit LeNet-like ConvNet to images
```python
from csxdata import CData

from brainforge import Network
from brainforge.layers import (DenseLayer, DropOut, Activation,
                               PoolLayer, ConvLayer)

dataroot = "path/to/pickled/gzipped/tuple/of/X/Y/ndarrays.pkl.gz"
images = CData(dataroot, indeps=0, headers=None)

inshape, outshape = images.neurons_required

model = Network(inshape, layers=(
    ConvLayer(nfilters=10, filterx=3, filtery=3),
    PoolLayer(fdim=2),
    DropOut(0.5),
    Activation("relu"),
    ConvLayer(nfilters=10, filterx=5, filtery=5),
    PoolLayer(fdim=3),
    Activation("relu"),
    DenseLayer(120, activation="tanh"),
    DropOut(0.5),
    DenseLayer(outshape, activation="softmax")
))
model.finalize(cost="xent", optimizer="rmsprop")
X, Y = images.table("learning")
valid = images.table("testing")
model.fit(X, Y, batch_size=20, epochs=30, validation=valid,
          monitor=["acc"])
```

###Fit LSTM to textual data
```python
from csxdata import Sequence

from brainforge import Network
from brainforge.layers import DenseLayer, LSTM

datapath = "path/to/text/file.txt"
# Chop up the data into three-character 'ngrams'
# (a character-level RNN would use n_gram=1) 
# Sequence data is ordered. In this case, the
# timestep parameter specifies how many ngrams
# are in X before Y is set. Consider the following case:
# [Mar][y h][ad ][a l][itt][le ][lam]
# [     THESE NGRAMS ALL GO TO X    ]
# The next ngram, [b ,] is the Y corresponding to the
# above X. Thus X is 3-dimensional, conventionally:
# (timestep, batch_size, data_dimensionality),
# Where data_dimensionality either comes from either
# the one-hot representation of every individual ngram,
# or some kind of embedding into k-dimensional continous
# space.
seq = Sequence(datapath, n_gram=3, timestep=7)
inshape, outshape = seq.neurons_required
model = Network(inshape, layers=(
    LSTM(120, activation="relu", return_seq=True),
    LSTM(60, activation="relu", return_seq=False),
    DenseLayer(120, activation="tanh"),
    DenseLayer(outshape, activation="softmax")
))
model.finalize(cost="xent", optimizer="rmsprop")
X, Y = seq.table("learning", shuff=True)
valid = seq.table("testing", shuff=True)
model.fit(X, Y, batch_size=32, epochs=100,
          monitor=["acc"], validation=valid)
```
