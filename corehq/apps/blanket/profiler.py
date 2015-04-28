import cProfile, pstats
from six import StringIO


class Profiler(object):
    """
    Provides the ability to save all models at the end of the request. We cannot save during
    the request due to the possibility of atomic blocks and hence must collect data and perform
    the save at the end.
    """

    def __init__(self):
        self.pythonprofiler = cProfile.Profile()

    def start_python_profiler(self):
        self.pythonprofiler.enable()

    def stop_python_profiler(self):
        self.pythonprofiler.disable()

    def finalize(self):
        s = StringIO()
        ps = pstats.Stats(self.pythonprofiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        profile_text = s.getvalue()
        profile_text = "\n".join(
            profile_text.split("\n")[0:256])  # don't record too much because it can overflow the field storage size
        return profile_text
