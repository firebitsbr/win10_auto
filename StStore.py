"""
Copyright 2019 FireEye, Inc.

Author: Omar Sardar <omar.sardar@fireeye.com>
Name: StStore.py

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging

from Tools import Tools


class StStore(Tools):
    """
    The StStore class corresponds to the Windows 10 ST_STORE structure. The
    ST_STORE structure is nested within SMKM_STORE and represents a single store.
    The nested structure ST_DATA_MGR is the only field of interest in page retrieval.
    """
    def __init__(self, loglevel=logging.INFO):
        self.tools = super(StStore, self).__init__()
        self.logger = logging.getLogger("ST_STORE")
        self.logger.setLevel(loglevel)
        self.fe = self.get_flare_emu()
        return

    def _dump(self):
        """
         Architecture agnostic function used to dump all located fields.
         """
        arch = 'x64' if self.Info.is_64bit() else 'x86'
        self.logger.info("StDataMgr: {0:#x}".format(self.Info.arch_fns[arch]['ss_stdatamgr'](self)))
        return

    @Tools.Info.arch32
    @Tools.Info.arch64
    def ss_stdatamgr(self):
        """
        This nested structure contains information used to correlate an SM_PAGE_KEY with a chunk key,
        from which a compressed page's location can be derived from within a region of
        MemCompression.exe. See ST_DATA_MGR for additional information. This function relies on the
        second argument for StDmStart remaining constant. Disassembly snippet from Windows 10 1809 x86
        shown below.

        StStart+27A     lea     edx, [esi+38h]
        StStart+27D     mov     ecx, esi
        StStart+27F     call    ?StDmStart@?$ST_STORE@USM_TRAITS@@@@SGJPAU1@PAU_ST_DATA_MGR@1@...
        """
        (startAddr, endAddr) = self.locate_call_in_fn("?StStart", "StDmStart")
        self.fe.iterate([endAddr], self.tHook)
        reg_dx = 'rdx' if self.Info.is_64bit() else 'edx'
        return self.fe.getRegVal(reg_dx)
