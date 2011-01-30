from zope import interface
from zope.component.interfaces import IObjectEvent


class IInitAsync(interface.Interface):

    def init():
        """ init zc.async """


class IAsyncDatabase(interface.Interface):
    """ zc.async database """


class IAsyncService(interface.Interface):
    """Utility"""

    def getQueues():
        """Return the queue container."""

    def queueJob(func, context, *args, **kwargs):
        """Queue a job."""

    def queueSerialJobs(*job_infos):
        """Queue several jobs, to be run serially

        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueParallelJobs(*job_infos):
        """Queue several jobs, to be run in parallel

        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueJobInQueue(queue, quota_names, func, context, *args, **kwargs):
        """Queue a job in a specific queue.
        Looks into the kwargs for:
            plone.app.async.service.DEFERRED_JOB_KEY
        If it is present, use the value (datetime) to set
        the 'begin_after' queue.put argument to defer the job start
        """

    def queueSerialJobsInQueue(queue, quota_names, *job_infos, **kwargs):
        """Queue several jobs in a specific queue, to be run serially

        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueParallelJobsInQueue(queue, quota_names, *job_infos, **kwargs):
        """Queue several jobs in a specific queue, to be run in parallel

        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueDeferredJob(func, begin_after, context, *args, **kwargs):
        """Queue a job.
        begin_after : datetime after which the job can be launched
        """ 

    def queueDeferredJobInQueue(queue, quota_names, func, begin_after, context, *args, **kwargs):
        """Queue a job in a specific queue.
        Looks into the kwargs for:
            plone.app.async.service.DEFERRED_JOB_KEY
        If it is present, use the value (datetime) to set
        the 'begin_after' queue.put argument to defer the job start
        """ 

    def queueDeferredSerialJobsInQueue(queue, quota_names, begin_after, *job_infos):
        """Queue several jobs in a specific queue, to be run serially

        begin_after : datetime after which the job can be launched
        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueDeferredParallelJobsInQueue(queue, quota_names, begin_after, *job_infos):
        """Queue several jobs in a specific queue, to be run in parallel

        begin_after : datetime after which the job can be launched
        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueDeferredSerialJobs(begin_after, *job_infos):
        """Queue several jobs, to be run serially

        begin_after : datetime after which the job can be launched
        job_info is a tuple with (func, context, args, kwargs).
        """

    def queueDeferredParallelJobs(begin_after, *job_infos):
        """Queue several jobs, to be run in parallel

        begin_after : datetime after which the job can be launched
        job_info is a tuple with (func, context, args, kwargs).
        """


class IQueueReady(IObjectEvent):
    """Queue is ready"""


class QueueReady(object):
    interface.implements(IQueueReady)

    def __init__(self, object):
        self.object = object


class IJobSuccess(IObjectEvent):
    """Job was completed successfully"""


class JobSuccess(object):
    interface.implements(IJobSuccess)

    def __init__(self, object):
        self.object = object


class IJobFailure(IObjectEvent):
    """Job has failed"""


class JobFailure(object):
    interface.implements(IJobFailure)

    def __init__(self, object):
        self.object = object
