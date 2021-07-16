# python
from datetime import datetime
# django
from django.core.exceptions import ValidationError
from django.db.models import ObjectDoesNotExist, Count, Max
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
                return no_authority('群組')
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
    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        vote_no = data.get('voteNum')

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote)
        except:
            return err(Msg.Err.Vote.select)

        try:
            group_member = GroupMember.objects.get(group_no=vote.group_no, user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except:
            return err(Msg.Err.Group.member_read)

        if group_member.status_id != 1 and group_member.status_id != 4:
            return no_authority('群組')

        try:
            vote_option = VoteDateOption.objects.filter(
                vote_no=vote) if vote.option_type_id == 2 else VoteOption.objects.filter(vote_no=vote)
        except:
            return err(Msg.Err.Vote.option_read)

        try:
            vote_record = VoteRecord.objects.filter(vote_no=vote)
        except:
            return err(Msg.Err.Vote.record_read)

        vote_option_list = []
        for i in vote_option:
            vote_option_list.append(
                {
                    'voteItemNum': i.option_num,
                    'voteItemName': i.content

                }
            )
        response = {
            'title': vote.title,
            'voteItems': vote_option_list,
            'addItemPermit': bool(vote.is_add_option),
            'deadline': vote.end_time,
            'anonymous': bool(vote.is_anonymous),
            'chooseVoteQuantity': vote.multiple_choice,
            'voteCount': vote_record.count()
        }
        return success(response)

    # /vote/get_list/  -------------------------------------------------------------------------------------------------
    @action(detail=False)
    def get_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_no = data.get('groupNum')

        try:
            GroupMember.objects.get(group_no=group_no, user_id=uid, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except:
            return err(Msg.Err.Group.member_read)

        try:
            vote = Vote.objects.filter(group_no=group_no)
        except:
            return err(Msg.Err.Vote.select)

        vote_list = []
        for i in vote:
            try:
                vote_record = VoteRecord.objects.filter(vote_no=i.serial_no)
            except:
                return err(Msg.Err.Vote.record_read)

            try:
                is_vote = True if VoteRecord.objects.filter(vote_no=i.serial_no, user_id=uid).count() > 0 else False
            except:
                return err(Msg.Err.Vote.record_read)
            vote_list.append(
                {
                    'voteNum': i.serial_no,
                    'votersNum': vote_record.values('user_id').annotate(Count('user_id')).count(),
                    'title': i.title,
                    'isVoteType': is_vote
                }
            )

        response = {'vote': vote_list}
        return success(response)

    # /vote/vote/  -----------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def vote(self, request):
        data = request.data

        uid = data.get('uid')
        vote_no = data.get('voteNum')
        vote_option_no = data.get('voteItemNum')

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote)
        except:
            return err(Msg.Err.Vote.select)

        try:
            GroupMember.objects.get(user_id=uid, group_no=vote.group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except:
            return err(Msg.Err.Group.member_read)

        if len(vote_option_no) > vote.multiple_choice:
            return limit_vote()

        try:
            vote_record = VoteRecord.objects.filter(user_id=uid, vote_no=vote)
        except:
            return err(Msg.Err.Vote.record_read)

        record_list = []
        for i in vote_record:
            record_list.append(i.option_num)
            if i.option_num not in vote_option_no:
                try:
                    VoteRecord.objects.filter(user_id=uid, vote_no=vote, option_num=i.option_num).delete()
                except:
                    return err(Msg.Err.Vote.record_read)

        for i in vote_option_no:
            if i not in record_list:
                try:
                    VoteRecord.objects.create(vote_no=vote, option_num=i, user_id=uid, vote_time=datetime.now())
                except:
                    return err(Msg.Err.Vote.record_create)

        return success()

    # /vote/add_items/  ------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def add_items(self, request):
        data = request.data

        uid = data.get('uid')
        vote_no = data.get('voteNum')
        vote_items = data.get('voteItems')

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote)
        except:
            return err(Msg.Err.Vote.select)

        if vote.end_time < datetime.now():
            return vote_expired()

        try:
            GroupMember.objects.get(user_id=uid, group_no=vote.group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except:
            return err(Msg.Err.Group.member_read)

        vote_option = VoteDateOption if vote.option_type_id == 2 else VoteOption
        exist_no_list = []
        exist_cotent_list = []
        for i in vote_items:
            option_no = i['voteItemNum']
            content = i['voteItemName']
            try:
                vote_option.objects.get(vote_no=vote, option_num=option_no)
                exist_no_list.append(option_no)
                exist_cotent_list.append(content)
            except ObjectDoesNotExist:
                vote_option.objects.create(vote_no=vote, option_num=option_no, content=content)
        if len(exist_no_list) > 0:
            return vote_option_exist(f'{str(exist_no_list)}內容為{str(exist_cotent_list)}')
        return success

    # /vote/get_end_list/  ---------------------------------------------------------------------------------------------
    @action(detail=False)
    def get_end_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_no = data.get('groupNum')

        try:
            GroupMember.objects.get(user_id=uid, group_no=group_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except:
            return err(Msg.Err.Group.member_read)

        try:
            vote = Vote.objects.filter(group_no=group_no)
        except:
            return err(Msg.Err.Vote.select)

        vote_list = []
        for i in vote:
            if i.end_time < datetime.now():
                vote_no = i.serial_no
                vote_option = VoteDateOption if i.option_type_id == 2 else VoteOption

                try:
                    vote_record = VoteRecord.objects.filter(vote_no=vote_no).values('option_num').annotate(
                        count=Count('user_id'))
                    result_count = vote_record.filter().aggregate(vote_count=Max('count'))['vote_count']
                    result_data = vote_record.filter(count=result_count)
                except:
                    return err(Msg.Err.Vote.record_read)

                result = []
                for j in result_data:
                    try:
                        option_num = j['option_num']
                        result.append(
                            {
                                'voteResultNum': option_num,
                                'resultContent': vote_option.objects.get(vote_no=vote_no,
                                                                         option_num=option_num).content,
                            }
                        )
                    except ObjectDoesNotExist:
                        return not_found(Msg.NotFound.vote_option)
                    except:
                        return err(Msg.Err.Vote.select)

                vote_list.append(
                    {
                        'title': i.title,
                        'result': result,
                        'resultCont': result_count
                    }
                )

        return success({'vote': vote_list})
