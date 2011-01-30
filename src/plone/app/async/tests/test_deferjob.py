import datetime
import time
import pytz
import transaction
from zc.async.testing import wait_for_result, set_now, setUpDatetime, tearDownDatetime
from plone.app.async.tests.base import AsyncTestCase
from test_simplejob import searchForDocument


results = []
def job1(context):
    time.sleep(3)
    results.append(1)

def job2(context):
    time.sleep(2)
    results.append(2)

def job3(context):
    results.append(3)

def job4(context):
    time.sleep(3)
    results.append(4)

def job5(context):
    time.sleep(2)
    results.append(5)

def job6(context):
    results.append(6)

class TestDeferTiming(AsyncTestCase):
    """TestDeferSerialJob"""
    def testQueueDeferredSerialJobs(self):
        results[:] = []
        q = self.async.getQueues()['']
        transaction.commit()
        j1 = (job3, self.folder, (), {})
        j3 = (job2, self.folder, (), {})
        j2 = (job6, self.folder, (), {})
        j4 = (job5, self.folder, (), {})
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=2)
        jobs1 = self.async.queueDeferredSerialJobs(dt_two, j3, j1)
        jobs2 = self.async.queueDeferredSerialJobs(now, j4, j2)
        transaction.commit()
        wait_for_result(jobs1, seconds=20)
        wait_for_result(jobs2, seconds=20)
        self.assertEquals(results, [5, 6, 2, 3])

    def testQueueDeferredSerialJobsWithQuotas(self):
        q = self.async.getQueues()['']
        q.quotas.create('size1', size=1)
        q.quotas.create('size2', size=2)
        q.quotas.create('size4', size=4)
        j1 = (job3, self.folder, (), {})
        j3 = (job2, self.folder, (), {})
        j2 = (job6, self.folder, (), {})
        j4 = (job5, self.folder, (), {})
        # with only one queue
        results[:] = []
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=1)
        jobs1 = self.async.queueDeferredSerialJobsInQueue(q,('size1',), dt_two, j3, j1)
        jobs2 = self.async.queueDeferredSerialJobsInQueue(q,('size1',), dt_two, j4, j2)
        transaction.commit()
        wait_for_result(jobs2, seconds=20)
        self.assertEquals(results, [2, 3, 5, 6])
        # with two queue
        results[:] = []
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=1)
        jobs1 = self.async.queueDeferredSerialJobsInQueue(q,('size2',), dt_two, j3, j1)
        jobs2 = self.async.queueDeferredSerialJobsInQueue(q,('size2',), dt_two, j4, j2)
        transaction.commit()
        wait_for_result(jobs2, seconds=20)
        self.assertEquals(results, [2, 5, 3, 6])

    def testQueueDeferredParallelJobs(self):
        results[:] = []
        q = self.async.getQueues()['']
        transaction.commit()
        j1 = (job3, self.folder, (), {})
        j3 = (job2, self.folder, (), {})
        j2 = (job6, self.folder, (), {})
        j4 = (job5, self.folder, (), {})
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=2)
        jobs1 = self.async.queueDeferredParallelJobs(dt_two, j3, j1)
        jobs2 = self.async.queueDeferredParallelJobs(now, j4, j2)
        transaction.commit()
        wait_for_result(jobs1, seconds=20)
        wait_for_result(jobs2, seconds=20)
        self.assertEquals(results, [6, 5, 3, 2])


    def testQueueDeferredParallelJobsQuotas(self):
        """testQueueDeferredParallelJobs"""
        # Add new document
        results[:] = []
        q = self.async.getQueues()['']
        q.quotas.create('size1', size=1)
        q.quotas.create('size2', size=2)
        q.quotas.create('size3', size=3)
        q.quotas.create('size4', size=4)
        q.quotas.create('size5', size=5)
        q.quotas.create('size6', size=6)
        transaction.commit()
        j1 = (job1, self.folder, (), {})
        j2 = (job2, self.folder, (), {})
        j3 = (job3, self.folder, (), {})
        j4 = (job4, self.folder, (), {})
        j5 = (job5, self.folder, (), {})
        j6 = (job6, self.folder, (), {})
        #
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=5)
        jobs1 = self.async.queueDeferredParallelJobs(dt_two, j1, j2, j3)
        jobs2 = self.async.queueDeferredParallelJobs(now, j4, j5, j6)
        transaction.commit()
        time.sleep(15)
        self.assertEquals(results, [5, 6, 4, 2, 3, 1])
        #
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=3)
        results[:] = []
        transaction.commit()
        jobs1 = self.async.queueDeferredParallelJobsInQueue(q,('size2',),dt_two, j1, j2, j3)
        transaction.commit()
        jobs2 = self.async.queueDeferredParallelJobsInQueue(q,('size2',),now, j6, j5, j4)
        transaction.commit()
        time.sleep(15)
        self.assertEquals(results, [6, 5, 4, 1, 2, 3])
        #
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=3)
        results[:] = []
        transaction.commit()
        jobs1 = self.async.queueDeferredParallelJobsInQueue(q,('size3',),dt_two, j1, j2, j3)
        transaction.commit()
        jobs2 = self.async.queueDeferredParallelJobsInQueue(q,('size3',),now, j4, j5, j6)
        transaction.commit()
        time.sleep(15)
        self.assertEquals(results, [5, 6, 4, 1, 2, 3])
        #
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=3)
        transaction.commit()
        results[:] = []
        jobs1 = self.async.queueDeferredParallelJobsInQueue(q,('size4',),dt_two, j1, j2, j3)
        transaction.commit()
        jobs2 = self.async.queueDeferredParallelJobsInQueue(q,('size4',),now, j4, j5, j6)
        transaction.commit()
        time.sleep(15)
        self.assertEquals(results, [5, 6, 4, 1, 2, 3])
        #
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=3)
        results[:] = []
        transaction.commit()
        jobs1 = self.async.queueDeferredParallelJobsInQueue(q,('size6',),dt_two, j1, j2, j3)
        transaction.commit()
        jobs2 = self.async.queueDeferredParallelJobsInQueue(q,('size6',),now, j6, j5, j4)
        transaction.commit()
        time.sleep(15)
        self.assertEquals(results, [6, 5, 4, 1, 2, 3])
        #
        now        = datetime.datetime.now(pytz.UTC)
        dt_two     = now + datetime.timedelta(seconds=3)
        results[:] = []
        transaction.commit()
        jobs1 = self.async.queueDeferredParallelJobsInQueue(q,('size5',),dt_two, j1, j2, j3)
        transaction.commit()
        jobs2 = self.async.queueDeferredParallelJobsInQueue(q,('size5',),now, j6, j5, j4)
        transaction.commit()
        time.sleep(15)
        self.assertEquals(results, [6, 5, 4, 1, 2, 3])

class TestDeferJob(AsyncTestCase):
    """TestDeferJob"""

    def testQueueDeferredJobInQueue(self):
        """testQueueDeferredJobInQueue"""
        # Add new document
        queue = self.async.getQueues()['']
        queue.quotas.create('size2', size=2)
        self.folder.invokeFactory('Document', 'anid66', title='Foo', description='Foo', text='foo')
        self.folder.invokeFactory('Document', 'anid76', title='Foo', description='Foo', text='foo')
        self.folder.invokeFactory('Document', 'anid86', title='Foo', description='Foo', text='foo')
        doc1 = self.folder['anid66']
        doc2 = self.folder['anid76']
        doc3 = self.folder['anid86']
        now      = datetime.datetime(2006, 8, 10, 16, tzinfo=pytz.UTC)
        dt_one   = now + datetime.timedelta(hours=1)
        dt_two   = now + datetime.timedelta(hours=2)
        dt_three = now + datetime.timedelta(hours=3)
        dt_four  = now + datetime.timedelta(hours=4)
        dt_five  = now + datetime.timedelta(hours=5)
        dt_six   = now + datetime.timedelta(hours=6)
        set_now(now)
        job1 = self.async.queueDeferredJobInQueue(queue, ('size2',), searchForDocument, dt_three, doc1, doc1.getId())
        job2 = self.async.queueDeferredJobInQueue(queue, ('size2',), searchForDocument, dt_four , doc2, doc2.getId())
        job3 = self.async.queueDeferredJobInQueue(queue, ('size2',), searchForDocument, dt_one  , doc3, doc3.getId())
        transaction.commit()
        self.assertEquals(len(queue), 3)
        set_now(dt_two)
        transaction.commit()
        self.assertEquals(job3 is queue.claim(), True)
        self.assertEqual(wait_for_result(job3), 1)
        transaction.commit()
        self.assertEquals(len(queue), 2)
        self.assertTrue(queue.claim() is None)

    def testQueueDeferredJob(self):
        """testQueueDeferredJob"""
        # Add new document
        queue = self.async.getQueues()['']
        self.folder.invokeFactory('Document', 'anid66', title='Foo', description='Foo', text='foo')
        self.folder.invokeFactory('Document', 'anid76', title='Foo', description='Foo', text='foo')
        self.folder.invokeFactory('Document', 'anid86', title='Foo', description='Foo', text='foo')
        doc1 = self.folder['anid66']
        doc2 = self.folder['anid76']
        doc3 = self.folder['anid86']
        now      = datetime.datetime(2006, 8, 10, 16, tzinfo=pytz.UTC)
        dt_one   = now + datetime.timedelta(hours=1)
        dt_two   = now + datetime.timedelta(hours=2)
        dt_three = now + datetime.timedelta(hours=3)
        dt_four  = now + datetime.timedelta(hours=4)
        set_now(now)
        job1 = self.async.queueDeferredJob(searchForDocument, dt_three, doc1, doc1.getId())
        job2 = self.async.queueDeferredJob(searchForDocument, dt_four , doc2, doc2.getId())
        job3 = self.async.queueDeferredJob(searchForDocument, dt_one  , doc3, doc3.getId())
        transaction.commit()
        self.assertEquals(len(queue), 3)
        set_now(dt_two)
        transaction.commit()
        self.assertEquals(job3 is queue.claim(), True)
        self.assertEqual(wait_for_result(job3), 1)
        transaction.commit()
        self.assertEquals(len(queue), 2)
        self.assertTrue(queue.claim() is None)

    def tearDown(self):
        tearDownDatetime()
        AsyncTestCase.tearDown(self)

    def setUp(self):
        AsyncTestCase.setUp(self)
        setUpDatetime()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDeferJob))
    suite.addTest(makeSuite(TestDeferTiming))
    return suite
