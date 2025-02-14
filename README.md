# ShareMySky
Application code for UAI-IARA project Share My Sky 
Original code by Thomas Mazzi  thomasmazzi74@gmail.com 

Introduction
Imagine being in an unknown city without a map or needing help.
It would be difficult to orient yourself or give directions to the place,
right? GPS (Global Positioning System) is a bit like a super
powerful compass that always shows us the right way, no matter where in the world
we are. Thanks to a network of satellites that orbit the Earth, GPS
allows us to know our exact position at any time... or
almost. This system has revolutionized our way of life. Let's think
of smartphones: thanks to GPS we can use maps to reach a
destination, share our position with friends or find the
nearest restaurant, but GPS applications go much further: from
maritime and air navigation to logistics, from agriculture to
scientific research to requests for help as we sometimes see in the
mountains. In short, GPS has become an indispensable tool in
our daily life! An important tool also in the field of timely rescue.
GPS is a bit like a spatial triangulation system that works by
measuring the distance in time from the satellites above our heads. The
smartphone or navigator receives these signals and, calculating the time they
took to arrive, determines the position with extreme
precision.
There is no vacuum between the satellites and the receiver, in fact the signal path is
quite bumpy! One of the major obstacles that the signal must
overcome is the Earth's ionosphere, a layer of rarefied and ionized gas that
belongs to our atmosphere (from 60 km up to 700 km high). This
layer is constantly evolving and is kept excited by the Sun's rays,
flares and space weather events. The signals transmitted by the satellites
are deviated by free electrons, increasing the flight time and distorting
the GPS calculations. In addition, space weather events act as super
excitators of the ionosphere, modifying it in an unpredictable way and
increasing its absorption as well as scattering effects. To these
we must add other effects of gas physics that disturb the shape and
thickness of the ionosphere.
All this means GPS positioning errors and lack of
security.

The goal
Everything about the GPS signal is known at all times, it is all well described in the
specifications. It is therefore possible to receive a GPS signal from a satellite and
compare this with what is expected. The difference between the expected signal
and the received one, if the satellite is within optical range (in sight), is mainly attributable
to the excited state of the ionosphere. The errors introduced in the
position calculation and the Carry/Noise ratios (SNR normalized for
the bandwidth) received by the satellites, can be used to
study the ionosphere and its effects, trying to understand more about how
they act, about the correlations they have with space weather, in short
better understand this magical world, with the dual objective of being able to
understand more about space weather and contribute to the improvement of the
GPS system.

The experiment
In order to achieve the objective described above, the idea would be to
involve associations and people first, but to do this it is necessary to be able to perform measurements 
at low costs, with small spaces, accessible to
everyone, well supported in terms of software tools and above all robust and maintenance-free.
The instrument identified is a small GPS antenna (equipped with a UBLOX
7020 chip) designed for automotive and nautical applications, resistant to water and
weather (a small protective box does not hurt anyway) with the
dimensions of 5x4x2 cm to be positioned outside according to its
possibilities of visible sky (not everyone has a perfectly open sky).
The cost of the antenna is less than 20 euros to which you must add a
possible USB extension cable costing a few euros and a computer (even an
old one) connected to the internet with a LINUX system (a
raspberry could also work).
Each receiving station, depending on its own availability of sky
and time according to its own cutoff window, collects data on the signals
received from the satellites and sends them to a server where they are all conveyed.
In this way, users can also download data from other receiving stations and see:

1. what happened to the signals of different stations in correlation to events
2. make statistics
3. model the ionosphere having multiple points of view available at the same time
4. generate sw to share that allows to do studies on this data
The GPS system is coordinated by atomic clocks and the correlation of the data is
particularly precise.

The acquisition program has already been developed in python and at this
moment is running on an old PC. Obviously in this experimental
phase, it runs locally (there being only one station) but the
interesting data were not long in coming. In the graph below you can see the
moment in which the ionosphere disturbed the signal. Unfortunately, the
reason for these unexpected peaks is not yet clear, at that moment there were
no particular space weather events. There is a world to discover and we as
associations with an astronomical scientific target could do our part.
The sw generates text files of about 20MB per day that can also be used
with a simple excel or with a more advanced matlab or python. The choice of
the system depends on the user who, once the sw has been developed, can share it
with others.

In Conclusion
If you want to participate in this experiment you need to have:
1. a place with a minimum of sky available, even a
window in the city is fine
2. internet access
3. be able to use a computer
4. have a minimum amount of money available to purchase the system
5. desire, desire and desire to investigate these topics

