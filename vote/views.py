# python
from datetime import datetime
# django
from django.core.exceptions import ValidationError
from django.db.models import ObjectDoesNotExist
# rest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# my day
from vote.serializer import VoteSerializer
from api.models import Vote, VoteOption, VoteDateOption, VoteRecord, GroupMember, Group, Account
from api.response import *


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
            return not_found(Msg.NotFound.group)
        try:
            group_member = GroupMember.objects.filter(user=uid, group_no=group_no, status=1)
            group_manager = GroupMember.objects.filter(user=uid, group_no=group_no, status=4)
        except:
            return err(Msg.Err.Group.member_read)

        if len(group_member) <= 0 and len(group_manager) <= 0:
            return not_found(Msg.NotFound.not_in_group)

        try:
            vote = Vote.objects.create(group_no=group, option_type_id=option_type_id,
                                       founder=Account.objects.get(user_id=uid), title=title,
                                       found_time=datetime.now(), end_time=deadline, is_add_option=is_add_item_permit,
                                       is_anonymous=is_anonymous, multiple_choice=multiple_choice)
        except:
            return err(Msg.Err.Vote.create)

        if option_type_id == 1:
            vote_option = VoteOption
        elif option_type_id == 2:
            vote_option = VoteDateOption
        else:
            return option_type_not_exist()

        for i in vote_items:
            try:
                option_no = int(i.get('voteItemNum'))
                content = str(i.get('voteItemName'))
                vote_option.objects.create(vote_no=vote, option_num=option_no, content=content)
            except:
                return err(Msg.Err.Vote.option_create + '-no:' + str(i.get('voteItemNum')))

        return success()

    # /vote/edit/  -----------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def edit(self, request):
        data = request.data

        uid = data.get('uid')
        vote_no = data.get('voteNum')
        title = data.get('title')
        vote_items = data.get('voteItems')
        deadline = data.get('deadline')
        is_add_item_permit = data.get('isAddItemPermit')
        is_anonymous = data.get('isAnonymous')
        multiple_choice = data.get('chooseVoteQuantity')

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except:
            return not_found(Msg.NotFound.not_in_group)

        try:
            vote_record = VoteRecord.objects.filter(vote_no=vote)
        except:
            return err(Msg.Err.Vote.record_read)

        if len(vote_record) > 0:
            return can_not_edit()

        vote_type = vote.option_type_id

        if vote.founder.user_id != uid:
            try:
                group_member = GroupMember.objects.filter(user=uid, group_no=vote.group_no)
            except:
                return err(Msg.Err.Group.member_read)

            if len(group_member) <= 0:
                return not_found(Msg.NotFound.not_in_group)
            else:
                return no_authority()

        if title is not None and title != vote.title:
            vote.title = title
        if len(vote_items) < 1:
            return no_item()
        else:
            if vote_type == 1:
                vote_option = VoteOption
            elif vote_type == 2:
                vote_option = VoteDateOption
            else:
                return option_type_not_exist()

            vote_option_delete = vote_option.objects.filter(vote_no=vote_no)
            vote_option_backup = []
            for i in vote_option_delete:
                vote_option_backup.append(i)
            vote_option_delete.delete()

            for i in vote_items:
                try:
                    option_no = int(i.get('voteItemNum'))
                    content = str(i.get('voteItemName'))
                    vote_option.objects.create(vote_no=vote, option_num=option_no, content=content)
                except ValidationError:
                    try:
                        for j in vote_option_backup:
                            vote_option.objects.create(vote_no=j.vote_no, option_num=j.option_num, content=j.content)
                    except:
                        return err(Msg.Err.Vote.option_err)
                    return err(Msg.Err.Vote.type[vote_type])
                except:
                    return err(Msg.Err.Vote.option_err + '，' + Msg.Err.Vote.option_create + '-no:' + str(option_no))

        if deadline is not None and deadline != vote.end_time:
            vote.end_time = deadline
        if is_add_item_permit is not None and is_add_item_permit != vote.is_add_option:
            vote.is_add_option = is_add_item_permit
        if is_anonymous is not None and is_anonymous != vote.is_anonymous:
            vote.is_anonymous = is_anonymous
        if multiple_choice is not None and multiple_choice != multiple_choice:
            vote.multiple_choice = multiple_choice
        vote.save()
        return success()

    # /vote/delete/  ---------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def delete(self, request):
        data = request.data

        uid = data.get('uid')
        vote_no = data.get('voteNum')

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote)
        except:
            return err(Msg.Err.Vote.select)

        if vote.founder.user_id != uid:
            try:
                group_member = GroupMember.objects.filter(user_id=uid, group_no=vote.group_no)
            except:
                return err(Msg.Err.Group.member_read)
            if len(group_member) > 0:
                return no_authority()
            else:
                return not_found(Msg.NotFound.user_vote)

        try:
            vote_record = VoteRecord.objects.filter(vote_no=vote)
        except:
            return err(Msg.Err.Vote.record_read)
        try:
            vote_option = VoteOption.objects.filter(vote_no=vote)
        except:
            return err(Msg.Err.Vote.option_read)
        try:
            vote_date_option = VoteDateOption.objects.filter(vote_no=vote)
        except:
            return err(Msg.Err.Vote.date_option_read)
        try:
            vote_record.delete()
            vote_option.delete()
            vote_date_option.delete()
            vote.delete()
        except:
            return err(Msg.Err.Vote.data_delete)
        return success()

# /vote/get/  ------------------------------------------------------------------------------------------------------
# /vote/get_list/  -------------------------------------------------------------------------------------------------
# /vote/vote/  -----------------------------------------------------------------------------------------------------
# /vote/add_items/  ------------------------------------------------------------------------------------------------
# /vote/end/  ------------------------------------------------------------------------------------------------------
