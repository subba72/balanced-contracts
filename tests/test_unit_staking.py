from unittest import mock
from unittest.mock import patch
import pprint
from iconservice import Address, IconScoreException, IconScoreBase
from tbears.libs.scoretest.patch.score_patcher import get_interface_score, ScorePatcher
from tbears.libs.scoretest.score_test_case import ScoreTestCase
from pprint import pprint
from core_contracts.staking.staking import Staking
from core_contracts.staking.staking import InterfaceSystemScore
from core_contracts.staking.staking import sICXTokenInterface
from core_contracts.staking.utils.checks import SenderNotScoreOwnerError

EXA = 10 ** 18
DENOMINATOR = 10 ** 18


class Mock_Staking:

    def __init__(self, sICXInterface_address=None, _to=None, return_balanceOf=None, _amount=None, _data=None):
        self.sICX_address = sICXInterface_address
        outer_class = self

        class Mock_sICXTokenInterface:
            def __init__(self):
                self.balance = {}

            def balanceOf(self, _to):
                return self.balance.get(_to, 0)

            def mintTo(self, _to, _amount, _data):
                self.balance[_to] = self.balance.get(_to, 0) + _amount

            def burn(self, _amount):
                pass

            def transfer(self, _to: Address, _value: int, _data: bytes = None):
                self.balance[_to] = self.balance.get(_to, 0) + _amount

        self.mock_sICX = Mock_sICXTokenInterface()
        self.mock_sICX.balanceOf(_to)

    def create_interface_score(self, address, score):
        if address == self.sICX_address:
            return self.mock_sICX

        else:
            raise NotImplemented()

    def getIISSInfo(self):
        # print("next called")
        return {"nextPRepTerm": 1}

    def getPReps(self, x, y):
        # print("next called 1")
        return {"blockHeight": "0x246e21f", "startRanking": "0x1", "totalDelegated": "0x1442e60d8b6b6149d5e41e2",
                "totalStake": "0x15a91f6a769bc3588297b7a", "preps": [
                {"address": "hxf5a52d659df00ef0517921647516daaf7502a728", "status": "0x0", "penalty": "0x0",
                 "grade": "0x0", "name": "binance node", "country": "CYM", "city": "George town", "stake": "0x0",
                 "delegated": "0x2bcff93c61327dd1af4bc5", "totalblocks": "0x718e4c", "validatedblocks": "0x71887c",
                 "unvalidatedsequenceblocks": "0x0", "irep": "0x21e19e0c9bab2400000",
                 "irepupdateblockheight": "0x1cf1960", "lastgenerateblockheight": "0x246e1f0",
                 "blockheight": "0x1cf1960", "txindex": "0x1",
                 "nodeaddress": "hxf0bc67e700af57efc0a9140948c5678c50669f36", "email": "poolvip@binance.com",
                 "website": "https://binance.com", "details": "https://binance.com/json",
                 "p2pEndpoint": "170.106.8.247:7100"}]}

    def setStake(self, _stake_value):
        pass

    def getStake(self, address):
        return {'unstakes': {
            -1: {'unstakeBlockHeight': 10000}
        }}

    def setDelegation(self, a):
        pass


class Test_unit_staking(ScoreTestCase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.test_account3 = None

    def setUp(self):
        super().setUp()

        self._owner = self.test_account1
        self._to = self.test_account2
        self.test_account3 = Address.from_string(f"hx{'12331' * 8}")
        self._prep1 = self.test_account3
        self._prep2 = Address.from_string(f"hx{'12341' * 8}")
        self._prep3 = Address.from_string(f"hx{'12c31' * 8}")
        self._prep4 = Address.from_string(f"hx{'12cc1' * 8}")
        self._prep5 = Address.from_string(f"hx{'02cc1' * 8}")
        self.mock_InterfaceSystemScore = Address.from_string('cx0000000000000000000000000000000000000000')
        self.mock_sICXTokenInterface = Address.from_string('cx1000000000000000000000000000000000000000')

        with patch('core_contracts.staking.staking.IconScoreBase.create_interface_score',
                   return_value=Mock_Staking()) as mock_initialization:
            score = self.get_score_instance(Staking, self._owner)

        mock_initialization.assert_called_with(self.mock_InterfaceSystemScore, InterfaceSystemScore)

        self.score = score
        # self.set_msg(self._owner)

    def test_name(self):
        self.set_tx(self._owner)
        # print(self.score.name())
        self.assertEqual('Staked ICX Manager', self.score.name())

    def test_getTodayRate(self):
        DENOMINATOR = 10 ** 18
        self.set_msg(self._owner)
        # print(self.score.getTodayRate())

        self.assertEqual(DENOMINATOR, self.score.getTodayRate())

    def test_toggleStakingOn(self):
        self.set_msg(self._owner)
        # self.score.toggleStakingOn()

        self.score.toggleStakingOn()
        # NOT OWNER
        self.set_msg(self._to)
        with self.assertRaises(SenderNotScoreOwnerError) as err:  # executes when assertionError is raised
            # print(str(err), 'method called by other than owner raise Error')
            self.score.toggleStakingOn()

    def test_setSicxAddress(self):
        self.set_msg(self._owner)
        self.score.setSicxAddress(self.mock_sICXTokenInterface)
        self.set_msg(self._to)
        # self.score.setSicxAddress(self.mock_sICXTokenInterface)

        with self.assertRaises(SenderNotScoreOwnerError) as err:
            self.score.setSicxAddress(self.mock_sICXTokenInterface)
        self.set_msg(self._owner)
        try:
            self.score.setSicxAddress(self._to)  # EOA sent instead of contract
        except IconScoreException as err:

            self.assertEqual('StakedICXManager: Address provided is an EOA address. A contract address is required.',
                             err.message)

    def test_getSicxAddress(self):
        self.set_msg(self._owner)
        self.score.setSicxAddress(self.mock_sICXTokenInterface)
        self.assertEqual(self.mock_sICXTokenInterface, self.score.getSicxAddress())

    def test_setUnstakeBatchLimit(self):
        self.set_msg(self._owner)
        self.score.setUnstakeBatchLimit(2)

    def test_getUnstakeBatchLimit(self):
        print(self.score.getUnstakeBatchLimit())

    def test_getPrepList(self):
        print(self.score.getPrepList())

    def test_getUnstakingAmount(self):
        print(self.score.getUnstakingAmount())

    def test_getTotalStake(self):
        print(self.score.getTotalStake())

    def test_getLifetimeReward(self):
        print(self.score.getLifetimeReward())

    def test_getTopPreps(self):
        self.score.getTopPreps()

    def test_getAddressDelegations(self):
        self.set_msg(self._owner)
        self.score.setSicxAddress(self.mock_sICXTokenInterface)
        _bln = 15 * 10 ** 18
        self.score._rate.set(1 * EXA)

        self.score._address_delegations = {
            str(self._owner): f'{self._prep1}:50.{self._prep2}:50.',
            str(self._to): f'{self._prep1}:50.{self._prep2}:40.{self._prep3}:10.',
            # has to end with '.' to get full value

        }
        expected_value = {
            str(self._prep1): 7,
            str(self._prep2): 6,
            str(self._prep3): 1,
        }

        _address = self._to
        self.patch_internal_method(self.mock_sICXTokenInterface, 'balanceOf', lambda _address: _bln)
        print(self.score.getAddressDelegations(_address))
        return_value = self.score.getAddressDelegations(_address)
        self.assert_internal_call(self.mock_sICXTokenInterface, 'balanceOf', _address)

        self.assertEqual(expected_value, return_value)

    def test_getPrepDelegations(self):
        self.score.getPrepDelegations()

    def test_getUnstakeInfo(self):
        self.score.getUnstakeInfo()

    def test_getUserUnstakeInfo(self):
        print(self.score.getUserUnstakeInfo(self._owner))

    def test_claimUnstakedICX(self):
        self.score.claimUnstakedICX(self._owner)

    def test_claimableICX(self):
        print(self.score.claimableICX(self._owner))


    def test_stakeICX(self):
        self.set_msg(self._owner, 400 * EXA)
        self.score._sICX_address.set(self.mock_sICXTokenInterface)
        self.score.toggleStakingOn()

        self.score._rate.set(1 * EXA)
        _bln = 400 * EXA
        amount = 50 * EXA
        Data = b'StakingICX'
        _to = self._to
        print("getTotalStake: ", self.score.getTotalStake())
        top_prep = {str(self._prep1), str(self._prep2), str(self._prep3), str(self._prep4)}
        self.score._top_preps = top_prep
        self.score._prep_list = {str(self._prep1), str(self._prep2), str(self._prep3), str(self._prep4),
                                 str(self._prep5)}

        patch_sicx_interface = Mock_Staking(sICXInterface_address=self.mock_sICXTokenInterface,
                                            _to=self._owner,
                                            return_balanceOf=_bln,
                                            _amount=amount,
                                            _data=Data).create_interface_score
        with patch.object(self.score, 'create_interface_score', wraps=patch_sicx_interface) as object_patch:
            val = self.score.stakeICX(self._owner)
            # self.score.stakeICX(self._owner)

            object_patch.assert_called_with(self.mock_sICXTokenInterface, sICXTokenInterface)
            # object_patch.assert_called_with(self.mock_sICXTokenInterface, 'balanceOf', self._owner)
            # self.score.TokenTransfer.assert_called_with(self._to, expected_value,
            #                                             f'{expected_value // DENOMINATOR} sICX minted to {self._to}')
            # self.assertEqual(expected_value, self.score._sICX_supply.get())

            # print(val)

            # print(self.score._get_address_delegations_in_per(self._to))
            print('---')
            mock_obj = Mock_Staking()
            print(mock_obj.mock_sICX.balanceOf(self._owner))
            print("\ngetTotalStake: ", self.score.getTotalStake())
            print("\ngetAddressDelegations: ", self.score.getAddressDelegations(self._owner))

            print("\ngetPrepDelegations: ", self.score.getPrepDelegations())

            print("\n_address_delegations: ", self.score._address_delegations[str(self._owner)])
            print('----')

            self.assertEqual(400 * EXA, self.score.getTotalStake())
            self.assertEqual(400 * EXA, val)
            _distribute_evenly = (100 * EXA) // 4

            self.assertEqual(_distribute_evenly,
                             self.score._get_address_delegations_in_per(self._owner)[str(self._prep1)])
            self.assertEqual(_distribute_evenly,
                             self.score._get_address_delegations_in_per(self._owner)[str(self._prep2)])
            self.assertEqual(_distribute_evenly,
                             self.score._get_address_delegations_in_per(self._owner)[str(self._prep3)])
            self.assertEqual(_distribute_evenly,
                             self.score._get_address_delegations_in_per(self._owner)[str(self._prep4)])
            try:
                self.assertEqual(_distribute_evenly,
                                 self.score._get_address_delegations_in_per(self._owner)[str(self._prep5)])
            except KeyError:
                print(f'{self._prep5} is not a top prep thus does not has equal delegation per')
            top_prep_del_amoount = (_distribute_evenly * 400 * EXA) // (100 * EXA)

            self.assertEqual(top_prep_del_amoount, self.score.getPrepDelegations()[str(self._prep1)])
            self.assertEqual(top_prep_del_amoount, self.score.getPrepDelegations()[str(self._prep2)])
            self.assertEqual(top_prep_del_amoount, self.score.getPrepDelegations()[str(self._prep3)])
            self.assertEqual(top_prep_del_amoount, self.score.getPrepDelegations()[str(self._prep4)])
            self.assertEqual(0, self.score.getPrepDelegations()[str(self._prep5)]) # self._prep5 is not top prep so 0

            self.set_msg(self._owner,500*EXA)

            val1 = self.score.stakeICX(self._owner)
            delta_icx = 900*EXA - 400*EXA
            _distributed_votes_per =self.score._get_address_delegations_in_per(self._owner)[str(self._prep1)]
            print('_distributed_per',_distributed_votes_per)
            print('delta_icx',delta_icx)
            top_prep_del_amoount1= (_distributed_votes_per * delta_icx) // (100 * EXA) +top_prep_del_amoount
            print('---')
            print("\ngetTotalStake: ", self.score.getTotalStake())
            print("\ngetAddressDelegations: ", self.score.getAddressDelegations(self._owner))

            print("\ngetPrepDelegations: ", self.score.getPrepDelegations())

            print("\n_address_delegations: ", self.score._address_delegations[str(self._owner)])
            print('----', val1)

        self.assertEqual((400 * EXA+ 500* EXA), self.score.getTotalStake())
        self.assertEqual(500 * EXA, val1)
        self.assertEqual(top_prep_del_amoount1, self.score.getPrepDelegations()[str(self._prep1)])

    def test_transferUpdateDelegations(self):
        try:
            self.score.transferUpdateDelegations()
        except IconScoreException as err:
            self.assertEqual('StakedICXManager: ICX Staking SCORE is not active.', err.message)

        self.set_msg(self._owner, 12* EXA)
        self.score._sICX_address.set(self.mock_sICXTokenInterface)
        self.score.toggleStakingOn()
        # CALLING FUNCTION WITH OWNER ADDRESS
        try:
            self.score.transferUpdateDelegations(self._owner, self._to, 10 * 10 ** 18)
        except IconScoreException as err:
            self.assertEqual("StakedICXManager: Only sicx token contract can call this function.", err.message)

        # self.set_msg(self.mock_sICXTokenInterface, 16 * EXA)  # SETTING SICXINTERFACE ADDRESS AS IN CALLING FUNCTION
        _bln = 10 * EXA
        amount = 25 * EXA
        Data = b'StakingICX'
        self.score._rate.set(1 * EXA)

        top_prep = {str(self._prep1), str(self._prep2), str(self._prep3), str(self._prep4)}
        self.score._top_preps = top_prep
        self.score._prep_list = {str(self._prep1), str(self._prep2), str(self._prep3), str(self._prep4),str(self._prep5)}

        print("\ngetPrepDelegations after assigning : ",self.score.getPrepDelegations())
        print(' self.score.getTotalStake(): ', self.score.getTotalStake())
        patch_sicx_interface = Mock_Staking(sICXInterface_address=self.mock_sICXTokenInterface,
                                            _to=self._owner,
                                            return_balanceOf=_bln,
                                            _amount=amount,
                                            _data=Data).create_interface_score
        with patch.object(self.score, 'create_interface_score', wraps=patch_sicx_interface) as object_patch:
            self.score.stakeICX(self._owner)
            print("\n after stake")
            print("\ngetAddressDelegations, owner: ",self.score.getAddressDelegations(self._owner))
            _owner_address_del_pref= self.score.getAddressDelegations(self._owner)

            print("\nprep delegation ",self.score.getPrepDelegations())

            object_patch.assert_called_with(self.mock_sICXTokenInterface, sICXTokenInterface)

            # object_patch(self.mock_sICXTokenInterface, self.score).transfer(self._to, 1 * EXA)


            #
            # print("---")
            print("\ngetAddressDelegations, _to : ",self.score.getAddressDelegations(self._to))

            self.set_msg(self.mock_sICXTokenInterface)
            self.score.transferUpdateDelegations(self._owner, self._to, 10 * 10 ** 18)
            print(' self.score.getTotalStake(): ', self.score.getTotalStake())

            print("\n after transferUpdateDelegations")

            print("\ngetAddressDelegations, _to : ", self.score.getAddressDelegations(self._to))
            _to_old_address_deleg= self.score.getAddressDelegations(self._to)
            _to_address_del_pref = self.score.getAddressDelegations(self._to)
            print("\nprep delegation ", self.score.getPrepDelegations())

            # THE TOTAL STAKE RAMAINS THE SAME THOUGH THE transferUpdateDelegations() IS CALLED
            self.assertEqual((12 * EXA  ), self.score.getTotalStake())
            print(' self.score.getTotalStake(): ', self.score.getTotalStake())

            # _owner PREFERENCE REPLICATED TO _to; BOTH HAVE SAME PREPS TO DELEGATE
            self.assertEqual(_to_address_del_pref.keys(), _owner_address_del_pref.keys())
            self.assertNotEqual(_to_address_del_pref, _owner_address_del_pref)

            self.set_msg(self._to, 40*EXA)
            self.score.stakeICX(self._to)
            print("\n after stake")
            print("\ngetAddressDelegations, _to : ", self.score.getAddressDelegations(self._to))
            print("\nprep delegation ", self.score.getPrepDelegations())

            _distribute_evenly = (40 * EXA) // 4  # TOP_PREP COUNT = 4
            print(' self.score.getTotalStake(): ', self.score.getTotalStake())

            # CHECKING _to DELEGATION VALUE UPDATED AFTER STAKING
            # THE PREP DELEGATION UPDATED WITH THE STAKING DONE BY _to
            self.assertEqual(_owner_address_del_pref[str(self._prep1)]+ _distribute_evenly, self.score.getPrepDelegations()[str(self._prep1)])
            self.assertEqual(_owner_address_del_pref[str(self._prep2)]+ _distribute_evenly, self.score.getPrepDelegations()[str(self._prep2)])
            self.assertEqual(_owner_address_del_pref[str(self._prep3)]+ _distribute_evenly, self.score.getPrepDelegations()[str(self._prep3)])
            self.assertEqual(_owner_address_del_pref[str(self._prep4)]+ _distribute_evenly, self.score.getPrepDelegations()[str(self._prep4)])
            self.assertEqual(0, self.score.getPrepDelegations()[str(self._prep5)])

            # TOTAL STAKE INCREASED WITH _owner AND _tO STAKING 12 AND 40 DURING THIS FN TEST
            self.assertEqual((12 * EXA + 40 *EXA), self.score.getTotalStake())
            _to_updated_address_deleg= self.score.getAddressDelegations(self._to)

            # CHECKING 40* EXA DISTRUBTED EQUALLY
            # BEFORE 0
            # AFTER 10000000000000000000
            self.assertNotEqual(_to_old_address_deleg, _to_updated_address_deleg)
            self.assertEqual(_to_old_address_deleg[str(self._prep1)]+_distribute_evenly, self.score.getAddressDelegations(self._to)[str(self._prep1)])
            # DONE FOR 1 PREP IS EQUAL THUS OTHER ARE ALSO EQUAL


            # TRANSFERING FROM _to TO _owner AGAIN AND VALIDATING ASSERTION





    def test_delegate(self):
        self.set_msg(self._owner)
        try:
            self.score.delegate()
        except IconScoreException as err:
            self.assertEqual('StakedICXManager: ICX Staking SCORE is not active.', err.message)

        self.score.toggleStakingOn()

        _bln = 100 * 10 ** 18

        self.score._rate.set(1 * EXA)

        self.score._address_delegations = {
            str(self._owner): f'{self._prep1}:50.{self._prep2}:50.',
            str(self._to): f'{self._prep1}:50.{self._prep2}:40.{self._prep3}:10.',

        }

        _user_delegations = [
            {'_address': 'hxe0cde6567eb6529fe31b0dc2f2697af84847f321', '_votes_in_per': 100 * 10 ** 18}]
        _to = self._owner

        self.score._sICX_address.set(self.mock_sICXTokenInterface)
        self.score._total_stake.set(1000 * 10 ** 18)

        # raise Exception("not completed")
        return_blnc = 20 * EXA
        amount = 50 * EXA
        Data = b'StakingICX'
        print(self.score._prep_delegations[self._owner])
        patch_sicx_interface = Mock_Staking(sICXInterface_address=self.mock_sICXTokenInterface,
                                            _to=_to,
                                            return_balanceOf=_bln,
                                            _amount=amount,
                                            _data=Data).create_interface_score
        with patch.object(self.score, 'create_interface_score', wraps=patch_sicx_interface) as object_patch:

            self.score.delegate(_user_delegations)
        # object_patch.assert_called_with(self.mock_InterfaceSystemScore, InterfaceSystemScore)
        object_patch.assert_called_with(self.mock_sICXTokenInterface, sICXTokenInterface)

    def test_tokenFallback(self):
        # CHECKING FOR STAKING ON
        self.set_msg(self._owner)
        try:
            self.score.tokenFallback()
        except IconScoreException as err:
            self.assertEqual('StakedICXManager: ICX Staking SCORE is not active.', err.message)
        # CHECKING FOR METHOD CALLED BY EOA ADDRESS
        self.score.toggleStakingOn()
        _from = self._owner
        _value = 100 * 10 ** 18
        _data = b"{\"method\": \"unstake\",\"user\":\"hx436106433144e736a67710505fc87ea9becb141d\"}"
        _to = self._to
        try:
            self.score.tokenFallback(_from, _value, _data)
        except IconScoreException as err:
            self.assertEqual("StakedICXManager: The Staking contract only accepts sICX tokens.", err.message)

        self.set_msg(self.mock_sICXTokenInterface)
        self.score._sICX_address.set(self.mock_sICXTokenInterface)
        patch_sicx_interface = Mock_Staking(sICXInterface_address=self.mock_sICXTokenInterface,
                                            _to=_to,
                                            return_balanceOf=_value,
                                            _amount=_value,
                                            _data=_data).create_interface_score
        with patch.object(self.score, 'create_interface_score', wraps=patch_sicx_interface) as object_patch:

            self.score.tokenFallback(_from, _value, _data)
        # object_patch.assert_called_with(self.mock_InterfaceSystemScore, InterfaceSystemScore)
        object_patch.assert_called_with(self.mock_sICXTokenInterface, sICXTokenInterface)
