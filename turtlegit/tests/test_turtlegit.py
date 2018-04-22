import posixpath
from turtlegit.cmdgit import status, init, add, commit, rmAll
from turtlegit.default_settings import Config, Logging
from turtlegit.run import app, createDir, deleteDir, getWorkspacePath, getDirFromWorkspace
import unittest
import tempfile
import logging as log
import os
import urllib
import io

class turtlegitTestCase(unittest.TestCase):

        
    def setUp(self):
        print("Tests setting up ...")
        log.basicConfig(level=log.getLevelName(Logging.LEVEL))
        app.config['TESTING'] = True
        self.app = app.test_client()
    
    def test_read_write_access(self):
        self.assertTrue(os.access(getWorkspacePath(), os.W_OK | os.X_OK))
    
    def test_creating_and_removing_directory(self):
        testPath=getDirFromWorkspace('create-and-remove-test')
        createDir(testPath)
        self.assertTrue(init(testPath))
        deleteDir(testPath)
    
    def test_create_new_repo(self):
        testPath = getDirFromWorkspace('new-repo-test-1-2-3-4')
        createDir(testPath)
        self.assertTrue(init(testPath))
        self.assertTrue(status(testPath))
        response = self.app.get('/new-repo-test-1-2-3-4', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = self.app.put('/new-repo-test-1-2-3-4?graph=http://localhost/new-repo-test-1-2-3/test.ttl', data=io.BytesIO(b'@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . rdf:rdf rdf:rdf rdf:rdf . '),content_type='text/turtle')
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/new-repo-test-1-2-3-4?graph=http://localhost/new-repo-test-1-2-3/test.ttl', data=io.BytesIO(b'@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . rdf:eat rdf:my rdf:foo . '),content_type='text/turtle')
        log.info(response.get_data().decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        deleteDir(testPath)
     
   
    def test_file_upload(self):
        testPath = getDirFromWorkspace('file-upload-test-1-2-3-4')
        createDir(testPath)
        self.assertTrue(init(testPath))
        self.assertTrue(status(testPath))
        response = self.app.post('file-upload-test-1-2-3-4/upload', data=dict(
            file=(io.BytesIO(b'@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . rdf:myMilkshake rdf:brings rdf:foo . '), 'test.ttl')
        ))
        self.assertEqual(response.status_code, 200)
        deleteDir(testPath)
        
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        print("Tests tearing down ...")
        
    


if __name__ == '__main__':
    unittest.main()