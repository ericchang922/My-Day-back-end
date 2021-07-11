# python
from datetime import datetime
# rest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# my day

from vote.serializer import VoteSerializer
from api.models import Vote, VoteOption, VoteDateOption, VoteRecord, GroupMember, Group, Account
# vote
from vote.response import *


class VoteViewSet(ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    # /vote/create_new/  -----------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def create_new(self, request):
        data = request.data

        uid = data.get('uid')
        group_no = data.get('groupNum')
        option_type_id = data.get('optionTypeId')
        title = data.get('title')
        vote_items = data.get('voteItems')
        deadline = data.get('deadline')
        is_add_item_permit = data.get('isAddItemPermit')
        is_anonymous = data.get('isAnonymous')
        multiple_choice = data.get('chooseVoteQuantity')

        if len(vote_items) < 1:
            return no_item()
        try:
            group = Group.objects.get(serial_no=group_no)
        except:
            return group_not_found()
        try:
            group_member = GroupMember.objects.filter(user=uid, group_no=group_no, status=1)
            group_manager = GroupMember.objects.filter(user=uid, group_no=group_no, status=4)
        except:
            return err(ErrMessage.group_member_read)

        if len(group_member) <= 0 and len(group_manager) <= 0:
            return not_in_group()

        try:
            vote = Vote.objects.create(group_no=group, option_type_id=option_type_id,
                                       founder=Account.objects.get(user_id=uid), title=title,
                                       found_time=datetime.now(), end_time=deadline, is_add_option=is_add_item_permit,
                                       is_anonymous=is_anonymous, multiple_choice=multiple_choice)
        except:
            return err(ErrMessage.vote_create)

        if option_type_id == 1:
            vote_option = VoteOption
        elif option_type_id == 2:
            vote_option = VoteDateOption
        else:
            return option_type_not_exist()

        for i in vote_items:
            try:
                vote_option.objects.create(vote_no=vote, option_num=int(i.get('voteItemNum')),
                                           content=str(i.get('voteItemName')))
            except:
                return err(ErrMessage.vote_option_create + str(i.get('voteItemNum')))

        return success()

    # /vote/edit/  -----------------------------------------------------------------------------------------------------
    # /vote/delete/  ---------------------------------------------------------------------------------------------------
    # /vote/get/  ------------------------------------------------------------------------------------------------------
    # /vote/get_list/  -------------------------------------------------------------------------------------------------
    # /vote/vote/  -----------------------------------------------------------------------------------------------------
    # /vote/add_items/  ------------------------------------------------------------------------------------------------
    # /vote/end/  ------------------------------------------------------------------------------------------------------
