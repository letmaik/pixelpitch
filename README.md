[![Build Status](https://travis-ci.org/neothemachine/pixelpitch.svg?branch=master)](https://travis-ci.org/neothemachine/pixelpitch)

http://neothemachine.github.io/pixelpitch/

Lists current cameras with their physical pixel sizes (pixel pitch).

Camera data is read from http://geizhals.at. Note that pixel pitch is calculated from resolution and sensor size, with a look up table if exact sensor size is not given (but instead a common size name). In 2015 geizhals.at added pixel pitch to their website as well, it may happen that the pixel pitch values slightly differ due to different formulas used.
