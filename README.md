# Amazon Alexa: request signature verification

Finally, a complete `Python` implementation for [signature verification][1] of [Amazon Alexa][0] service requests. It has been a *though* nut to crack, but once everything came together, reading the code is actually pretty self-explanatory.

I would like to thank [dizmo.com][5] for providing the financial support for this project, and generously allowing it to be open sourced: We hope that it will serve all the other companies and people out there, integrating their services with [Amazon Alexa][0].

The implementation is realized as a [hook][3] for the [Falcon][4] framework, which essentially is simply a function. Hence integrating it with other `Python` based frameworks should be pretty straight forward. Further, a local `redis` instance has been used for demonstration purposes, but in general any caching mechanism should do.

[0]: https://developer.amazon.com/alexa
[1]: https://developer.amazon.com/docs/custom-skills/host-a-custom-skill-as-a-web-service.html#checking-the-signature-of-the-request
[3]: https://falcon.readthedocs.io/en/stable/api/hooks.html
[4]: https://falconframework.org/
[5]: https://www.dizmo.com
