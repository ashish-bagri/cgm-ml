import os
import numpy as np
import h5py
import logging
import csv
import shutil


log = logging.getLogger(__name__)


class DataWriter:
    def __init__(self, config, run_id):
        base_dir = config.get('output', 'base_dir')
        self.base_dir = base_dir
        self.run_dir = os.path.join(base_dir, run_id)
        self.run_id = run_id
        self.initialize()

    def initialize(self):
        # create directory
        if not os.path.exists(self.run_dir):
            os.makedirs(self.run_dir)

    def write(self, qrcode, y_output, timestamp, pcd_paths):
        # qr code is the name of the file
        # xinput is ndarray
        # output is the target values
        qrcode_dir = os.path.join(self.run_dir, qrcode)
        if not os.path.exists(qrcode_dir):
            os.makedirs(qrcode_dir)
        subdir = os.path.join(qrcode_dir, str(timestamp))
        if not os.path.exists(subdir):
            os.makedirs(subdir)

        # target filename
        targetfilename = os.path.join(subdir, 'target.txt')
        with open(targetfilename, "w") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(y_output)

        pcd_dir = os.path.join(subdir, 'pcd')
        if not os.path.exists(pcd_dir):
            os.makedirs(pcd_dir)
        # copy over the pcd paths
        log.info("Copying pcd files for qrcode %s" % qrcode)
        for pcd_path in pcd_paths:
            fname = os.path.basename(pcd_path)
            dst = os.path.join(pcd_dir, fname)
            shutil.copyfile(pcd_path, dst)

    def wrapup(self):
        # write the readme file
        # zip and create simlink
        log.info("Going to zip the directory %s" % self.run_dir)
        zipfile = os.path.join(self.base_dir, self.run_id)
        shutil.make_archive(zipfile, 'zip', self.run_dir)

        # check existing simlink
        latestfilename = os.path.join(self.base_dir, 'latest.zip')
        if os.path.exists(latestfilename):
            os.unlink(latestfilename)

        # create a simlink
        simlinkfile = "%s.zip" % zipfile
        os.symlink(simlinkfile, latestfilename)
