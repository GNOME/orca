from orca.speech_generator import SpeechGenerator as BaseSpeechGenerator
import pyatspi

class SpeechGenerator(BaseSpeechGenerator):
    def _generateImage(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the image on the the object, if
        it exists.  Otherwise, an empty array is returned.
        """
        result = []
        try:
            image = obj.queryImage()
        except:
            pass
        else:
            args['role'] = pyatspi.ROLE_IMAGE
            result.extend(self.generate(obj, **args))
        return result

