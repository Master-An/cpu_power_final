"""TBSLTEUtil.py - TBSLTEUtil in MTFPy Util Library

TBSLTEUtil provides access to use TBSLTE module sepcific functions in MTFPy
based on user Requirement.

Author:
    Yi Sun<yisun@qti.qualcomm.com>

Release:
    2018/02/14 - Initial release.

Copyright:
    (c) Qualcomm Technologies, Inc. 2018
"""
import json
tbslte_import_error = None
try:
    import tbslte
except Exception as e:
    tbslte_import_error = e

class TBSLTEUtil(object):
    """TBSLTEUtil is wrapper class for tbslte

    TBSLTEUtil provides access to use TBSLTE module sepcific functions in MTFPy
    based on user Requirement.

    """

    _host_id = None
    _tbslte_handle = None
    _component_handles = {}

    def __init__(self, host_id=None):
        """create tbslte ojbect with specific TBSLTE server host id, """

        if tbslte_import_error is not None:
            raise TBSLTEUtilError(
                f'import tbslte occurs error: {tbslte_import_error}')

        self._initialize_tbslte_handle(host_id)

    def _initialize_tbslte_handle(self, host_id=None):
        """initialize TBSLTEUtil object handle

        Args:
            host_id (:class:`str`): : Required: Test base station hostname
                or station id. [Eg: 'qct-8001-enbu-0' or 8001]

        Raises:
            TBSLTEUtilError: if host_id didn't pass in or TBSLTE throw out exception
        """

        if host_id is None:
            raise TBSLTEUtilError(
                "Please provide Test base station hostname or station id")

        self._host_id = host_id

        try:
            self._tbslte_handle = tbslte.Client(host_id)
        except Exception as e:
            raise TBSLTEUtilError(str(e))
        return self._tbslte_handle

    def get_system_state(self):
        """Query the current tbslte system state:

        Returns:
            state (:class:`str`): TBSLTE state. can be One of:
                running, stopped, crashed
        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        try:
            state = self._tbslte_handle.get_system_state()
        except Exception as e:
            raise TBSLTEUtilError(str(e))
        return state

    def check_system_state(self, expected_state=None):
        """check TBSLTE system state

        check TBSLTE system state if it's expected sate.Return True or False

        Args:
            expected_state (:class:`str`): : Required: expected TBSLTE
                system state [Eg:running, stopped, crashed]

        Returns:
            retval (:class:`bool`):
                1 : TBSLTE system is on expected state
                0 : TBSLTE system isn't on expected state
        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if expected_state is None:
            expected_state = tbslte.STATE_RUNNING

        ret_val = 0
        current_state = self.get_system_state()
        if current_state == expected_state:
            ret_val = 1

        return ret_val

    def start_system(self):
        """start tbslte system

        start tbslte system by using previous deployed template.

        Returns:
            retval (:class:`int`):
                2 : tbslte system is already started.
                1 : start tbslte system successful.
                0 : start tbslte system failed.
        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if self.check_system_state(tbslte.STATE_RUNNING):
            return 2
        else:
            try:
                self._tbslte_handle.start_system()
            except Exception as e:
                raise TBSLTEUtilError(str(e))

        ret_val = 0
        if self.check_system_state(tbslte.STATE_RUNNING):
            ret_val = 1

        return ret_val

    def stop_system(self):
        """stop tbslte system

        stop ltbslte system

        Returns:
            retval (:class:`int`): None
                2:  tbslte system is already stopped
                1 : stop tbslte system successful
                0 : stop tbslte system failed

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if self.check_system_state(tbslte.STATE_STOPPED):
            return 2
        else:
            try:
                self._tbslte_handle.stop_system()
                self._component_handles = {}
            except Exception as e:
                raise TBSLTEUtilError(str(e))

        ret_val = 0
        if self.check_system_state(tbslte.STATE_STOPPED):
            ret_val = 1
        return ret_val

    def deploy_template(self, template_xml_path):
        """deploy and start tbslte template

        Args:
            template_xml (:class:`str`): : Required:
                The TBS server accessable template file path.
                the template will be deployed to the system regardless of its current state

        Returns:
            retval (:class:`boolean`): None
                1 : deploy and start tbslte system successful
                0 : deploy and start tbslte system failed

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception or
                          template_xml_path is empty.
        """

        if template_xml_path is None:
            raise TBSLTEUtilError(
                "template is None, please provide TBSLTE template")

        try:
            self._tbslte_handle.start_system(template=template_xml_path)
        except Exception as e:
            raise TBSLTEUtilError(str(e))

        ret_val = 0
        if self.check_system_state(tbslte.STATE_RUNNING):
            ret_val = 1

        return ret_val

    def send_testability_command(self, cmd):
        """send testability command

        Args:
            cmd (:class:`str`): :Required: The testability command to execute.
                it can also be a path to a file containing the command string to execute.

        Returns:
            result (:class:`dict`): return testability command output of that command.
                If executing only one testability command, returns the output of that command.

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if cmd is None:
            raise TBSLTEUtilError(
                "cmd is None, please provide TBSLTE testability command")

        try:
            resp = self._tbslte_handle.testability_command(cmd)
        except Exception as e:
            raise TBSLTEUtilError(str(e))

        result = None
        if resp is not None and 'output' in resp.keys():
            try:
                result = json.loads(resp['output'])
            except Exception as e:
                raise TBSLTEUtilError(
                    f"return resp didn't include correct json format: {e}")
        return result

    def get_component_count(self, component_name=None):
        """get component count

        Args:
            componentname (:class:`str`): tbslte.CELL:Required:
                component name: tbslte.BMSC, tbslte.GW, tbslte.MME, tbslte.ENB, tbslte.CELL

        Returns:
            cell_count (:class:`int`): 	The count of the given component type

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if component_name is None:
            component_name = tbslte.CELL

        try:
            cell_count = self._tbslte_handle.get_component_count(
                component_name)
        except Exception as e:
            raise TBSLTEUtilError(str(e))

        return cell_count

    def set_ior_on_cells(self, ior):
        """Set ior on all cells

        Set ior on all cells, all enabled diversities for each cell

        Args:
            ior (:class:`float`): 0: Required:
                PowerDbm value to set at a given tx/rx index for a given cell

        Returns:
            retval (:class:`bool`):  if set ior successful and get ior match to set ior
                return 1, others return 0

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if ior is None:
            raise TBSLTEUtilError(
                "ior is None, please provide panda ior")

        result = 1
        try:
            cellid = 0
            for cell in self._tbslte_handle.get_components(tbslte.CELL):
                cell.set_mimo_ior(ior)
                real_ior = self.get_ior(0, 0, cellid)
                cellid += 1
                if real_ior != ior:
                    result = 0
        except Exception as e:
            raise TBSLTEUtilError(str(e))

        return result

    def get_ior(self, tx, rx, cell_index):
        """Get ior value

        Get ior value from cell index transmitters index and receivers index

        Args:
            tx (:class:`str`): '*' :Required:  tx index at which the ior will be set.
                Default is '*' meaning all transmitters.
            rx (:class:`str`): '*': Required:  rx index at which the ior will be set.
                Default is '*' meaning all receivers.
            cell (:class:`int`): 0: Required: Index of cell of base station.

        Returns:
            ior (:class:`float`): PowerDbm value to set at a given tx/rx index for a given cell

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception

        """

        if tx is None:
            raise TBSLTEUtilError(
                "tx is None, please provide panda tx")
        if rx is None:
            raise TBSLTEUtilError(
                "rx is None, please provide panda rx")

        if cell_index is None:
            raise TBSLTEUtilError(
                "cell_index is None, please provide panda cell_index")

        try:
            cell_list = self._tbslte_handle.get_components(tbslte.CELL)
            ior = cell_list[int(cell_index)].get_mimo_ior(tx, rx, cell_index)
        except Exception as e:
            raise TBSLTEUtilError(str(e))
        return ior

    def get_cable_loss(self, link, antenna=None, cell=0):
        """Read additional cable loss value

        Read additional cable loss value for either downlink or uplink

        Args:
            link (:class:`tbslte.LINK`): :Required: ENUM LINK type - tbslte.UPLINK tbslte.DOWNLINK
            antenna (:class:`int`): : Optional: Antenna at which the loss value is read.
            cell (:class:`int`): 0: Optional: Index of cell of base station.

        Returns:
            loss_value (:class:`float`): A single float value if antenna index is specified
                else A dictionary with additional loss values for all antennae

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if (link is None or not isinstance(link, str)):
            raise TBSLTEUtilError(
                "link is not str , please provide str type for link  \
                UPLINK and DOWNLINK ")

        if str(link).lower() == 'downlink':
            link = tbslte.DOWNLINK
        elif str(link).lower() == 'uplink':
            link = tbslte.UPLINK
        else:
            raise TBSLTEUtilError(
                "link is not str , please provide str type for link  \
                UPLINK and DOWNLINK ")

        try:
            cell_list = self._tbslte_handle.get_components(tbslte.CELL)
            if antenna is None:
                loss_value = cell_list[int(cell)].get_cable_loss(link)
            else:
                loss_value = cell_list[int(cell)].get_cable_loss(
                    link, antenna=int(antenna))
        except Exception as e:
            raise TBSLTEUtilError(str(e))
        return loss_value

    def set_cable_loss(self, link, lost, antenna=None, cell=0):
        """Set additional cable loss value for either downlink or uplink

        Args:
            link (:class:`str`): :Required: str type - UPLINK DOWNLINK
            lost (:class:`float`): :Required: Loss in db to write at given antenna indices.
            antenna (:class:`int`): : Optional: Antenna at which the loss value is read.
            cell (:class:`int`): 0: Optional: Index of cell of base station.

        Returns:
            retval (:class:`bool`): set cable lost successful 1. others 0

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        if (link is None or not isinstance(link, str)):
            raise TBSLTEUtilError(
                "link is not str , please provide str type for link  \
                UPLINK and DOWNLINK ")

        if str(link).lower() == 'downlink':
            link = tbslte.DOWNLINK
        elif str(link).lower() == 'uplink':
            link = tbslte.UPLINK
        else:
            raise TBSLTEUtilError(
                "link is not str , please provide str type for link  \
                UPLINK or DOWNLINK ")

        if lost is None or not isinstance(lost, float):
            raise TBSLTEUtilError(
                "lost is not float , please provide float type for lost")

        if cell is None:
            cell = 0

        try:
            cell_list = self._tbslte_handle.get_components(tbslte.CELL)
            if (antenna is None or type(antenna) == 'NoneType'):
                cell_list[int(cell)].set_cable_loss(link, lost)
            else:
                cell_list[int(cell)].set_cable_loss(
                    link, lost, antenna=int(antenna))
        except Exception as e:
            raise TBSLTEUtilError(str(e))
        return 1

    def tbslte_dispatcher(self, method, *inputs):
        """TBSLTE commands dispatcher

        this function is universal function which access tbslte module any function
        return resp directly

        Args:
            method (:class:`str`): :Required: TBS raw api, please use go/tbsltedoc
                https://qct-artifactory.qualcomm.com/artifactory/
                tbs-content-browsing-local/sphinx_docs.zip!/sphinx_docs/index.html
                for api detail
            inputs (:class:`str`): :Required:
                TBS raw api input parameters.  it can be multi parameters.

        Returns:
            retval (:class:`dic`): return tbslte method

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception
        """

        try:
            result = getattr(self._tbslte_handle, method)(*inputs)
        except Exception as e:
            raise TBSLTEUtilError(str(e))
        return result

    def tbslte_component_dispatcher(self, component_name, component_index, method, *inputs):
        """TBSLTE component commands dispatcher

        TBSLTE component commands dispatcher allow user to send any component comment in tbslte module


        Args:
            component_name (:class:`str`): :Required:
                component name: tbslte.BMSC, tbslte.GW, tbslte.MME, tbslte.ENB, tbslte.CELL

            component_id (:class:`str`): None: Required:
                value can be 'all' component or component index

            method (:class:`str`): None:required
                TBS raw api, please use go/tbsltedoc
                https://qct-artifactory.qualcomm.com/artifactory/tbs-content-browsing-local
                /sphinx_docs.zip!/sphinx_docs/index.html
                for api detail

            inputs (:class:`str`): None
                TBS component raw api input parameters.  it can be multi parameters.

        Returns:
            result (:class:`dic`): return tbslte component method result dict

        Raises:
            TBSLTEUtilError: TBSLTE module throws out exception

        """

        try:
            if not (component_name in self._component_handles.keys()):
                self._component_handles[component_name] = self._tbslte_handle.get_components(
                    component_name)

            if str(component_index).lower() == 'all':
                for component_handle in self._component_handles[component_name]:
                    result = getattr(component_handle, method)(*inputs)
            else:
                result = getattr(
                    self._component_handles[component_name][component_index], method)(*inputs)

        except Exception as e:
            raise TBSLTEUtilError(str(e))

        return result

    def recover_system(self, retry=1):
        """TBSLTE recover system

        This function will restart ltetbs system again with maximum retry.

        Args:
            retry (:class:`int`): 1: Optional: maximum times to recover tbslte system.

        Returns:
            retval (:class:`bool`): 1: success to recover system, fail to recover system.
        """

        for i in range(0, retry):
            self.stop_system()
            if (self.start_system()):
                return 1
        return 0


class TBSLTEUtilError(Exception):
    """TBSLTEUtilError handles TBSLTEUtil  errors."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


if __name__ == '__main__':

    """unit test for tbslteutil"""
    # try:
    #     tbsltehandle = TBSLTEUtil(8158)

    # except TBSLTEUtilError:
    #     print("tbslte handle init failed")

    # result = tbsltehandle.get_cable_loss('UPLINK')
    # print(result)

    # result = tbsltehandle.set_cable_loss('UPLINK', 20.0)
    # print(result)

    # result = tbsltehandle.get_cable_loss('DOWNLINK')
    # print(result)

    # # tbsltehandle.get_system_state()
    # result = tbsltehandle.tbslte_dispatcher('get_system_state')
    # print(result)
    # result = tbsltehandle.send_testability_command(
    #     'MME COMMAND GET MME_QUERY_STATE')
    # print(result)
    # result = tbsltehandle.tbslte_dispatcher(
    #     'testability_command', 'MME COMMAND GET MME_QUERY_STATE')
    # print(result)

    # result = tbsltehandle.get_component_count()
    # print(result)

    # result = tbsltehandle.tbslte_dispatcher('get_component_count', tbslte.CELL)
    # print(result)
    # result = tbsltehandle.set_ior_on_cells(-51.0)
    # print(result)

    # result = tbsltehandle.tbslte_component_dispatcher(
    #     tbslte.CELL, 'all', 'set_mimo_ior', -50)
    # print(result)
    # result = tbsltehandle.tbslte_component_dispatcher(
    #     tbslte.CELL, 'all', 'get_mimo_ior')
    # print(result)
    # result = tbsltehandle.tbslte_component_dispatcher(
    #     tbslte.CELL, 1, 'get_mimo_ior')
    # print(result)

    # result = tbsltehandle.get_cable_loss('UPLINK')
    # print(result)

    # result = tbsltehandle.get_cable_loss('DOWNLINK', 1)
    # print(result)
    print(f'Error: {str(tbslte_import_error)}')
