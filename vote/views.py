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
from api.models import Vote, VoteOption, VoteDateOption, VoteRecord, GroupMember, Group, GroupLog, Account
from api.response import *


class VoteViewSet(ModelViewSet):
    queryset = Vote.objects.filter(serial_no=0)
    serializer_class = VoteSerializer

    # /vote/create_new/  ----------------------------------------------------------------------------------------------A
    @action(detail=False, methods=['POST'])
    def create_new(self, request):
        data = request.data

        uid = data['uid']
        group_no = data['groupNum']
        option_type_id = data['optionTypeId']
        title = data['title']
        vote_items = data['voteItems']
        deadline = data['deadline']
        is_add_item_permit = data['isAddItemPermit']
        is_anonymous = data['isAnonymous']
        multiple_choice = data['chooseVoteQuantity']

        if len(vote_items) < 1:
            return no_item(request)
        try:
            group = Group.objects.get(serial_no=group_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group, 'VO-A-001', request)  # -----------------------------------------------------001

        try:
            GroupMember.objects.get(user=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'VO-A-002', request)  # -----------------------------------------002

        try:
            vote = Vote.objects.create(group_no=group, option_type_id=option_type_id,
                                       founder=Account.objects.get(user_id=uid), title=title,
                                       found_time=datetime.now(), end_time=deadline, is_add_option=is_add_item_permit,
                                       is_anonymous=is_anonymous, multiple_choice=multiple_choice)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.create, 'VO-A-003', request)  # -----------------------------------------------003

        vote_option = VoteDateOption if option_type_id == 2 else VoteOption

        for i in vote_items:
            try:
                option_no = int(i['voteItemNum'])
                content = str(i['voteItemName'])
                vote_option.objects.create(vote_no=vote, option_num=option_no, content=content)
            except:
                return err(Msg.Err.Vote.option_create + '-no:' + str(i['voteItemNum']), 'VO-A-004', request)  # ---004

        try:
            GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid, trigger_type='I',
                                    do_type_id=5, new=title)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.log_create, 'VO-A-005', request)  # ------------------------------------------005

        return success(request=request)

    # /vote/edit/  ----------------------------------------------------------------------------------------------------B
    @action(detail=False, methods=['POST'])
    def edit(self, request):
        data = request.data

        uid = data['uid']
        vote_no = data['voteNum']
        title = data['title']
        vote_items = data['voteItems']
        deadline = data['deadline']
        is_add_item_permit = data['isAddItemPermit']
        is_anonymous = data['isAnonymous']
        multiple_choice = data['chooseVoteQuantity']
        old = None

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-B-001', request)  # -----------------------------------------------001

        if vote.end_time < datetime.now():
            return vote_expired(request)

        try:
            vote_record = VoteRecord.objects.filter(vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.record_read, 'VO-B-002', request)  # ------------------------------------------002

        if len(vote_record) > 0:
            return can_not_edit(request)

        group_no = vote.group_no.serial_no
        if vote.founder.user_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=group_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.not_in_group, request)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'VO-B-003', request)  # -------------------------------------003
            return no_authority('編輯投票', request)

        vote_type = vote.option_type_id
        if len(vote_items) < 1:
            return no_item(request)
        else:
            vote_option = VoteDateOption if vote_type == 2 else VoteOption

            vote_option_delete = vote_option.objects.filter(vote_no=vote_no)
            vote_option_backup = []
            for i in vote_option_delete:
                vote_option_backup.append(i)
            vote_option_delete.delete()

            for i in vote_items:
                try:
                    option_no = int(i['voteItemNum'])
                    content = str(i['voteItemName'])
                    vote_option.objects.create(vote_no=vote, option_num=option_no, content=content)
                except ValidationError:
                    try:
                        for j in vote_option_backup:
                            vote_option.objects.create(vote_no=j.vote_no, option_num=j.option_num, content=j.content)
                    except:
                        return err(Msg.Err.Vote.option_err, 'VO-B-004', request)  # -------------------------------004
                    return err(Msg.Err.Vote.type[vote_type], 'VO-B-005', request)  # ------------------------------005
                except:
                    return err(Msg.Err.Vote.option_err + '，' + Msg.Err.Vote.option_create + '-no:' + str(option_no),
                               'VO-B-006', request)  # ------------------------------------------------------------006

        if title is not None and title != vote.title:
            old = vote.title
            vote.title = title
        if deadline is not None and deadline != vote.end_time:
            vote.end_time = deadline
        if is_add_item_permit is not None and is_add_item_permit != vote.is_add_option:
            vote.is_add_option = is_add_item_permit
        if is_anonymous is not None and is_anonymous != vote.is_anonymous:
            vote.is_anonymous = is_anonymous
        if multiple_choice is not None and multiple_choice != multiple_choice:
            vote.multiple_choice = multiple_choice
        vote.save()

        try:
            group_log = GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid,
                                                trigger_type='U', do_type_id=5, new=title)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.log_create, 'VO-B-007', request)  # ------------------------------------------007

        if old is not None:
            group_log.old = old
            group_log.save()
        return success(request=request)

    # /vote/delete/  --------------------------------------------------------------------------------------------------C
    @action(detail=False, methods=['POST'])
    def delete(self, request):
        data = request.data

        uid = data['uid']
        vote_no = data['voteNum']

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-C-001', request)  # -----------------------------------------------001

        title = vote.title
        group_no = vote.group_no.serial_no
        if vote.founder.user_id != uid:
            try:
                group_member = GroupMember.objects.get(user_id=uid, group_no=group_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_vote, request)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'VO-C-002', request)  # -------------------------------------002
            if group_member.status_id != 4:
                return no_authority('刪除投票', request)

        try:
            vote_record = VoteRecord.objects.filter(vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.record_read, 'VO-C-003', request)  # ------------------------------------------003
        try:
            vote_option = VoteOption.objects.filter(vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.option_read, 'VO-C-004', request)  # ------------------------------------------004
        try:
            vote_date_option = VoteDateOption.objects.filter(vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.date_option_read, 'VO-C-005', request)  # -------------------------------------005
        try:
            vote_record.delete()
            vote_option.delete()
            vote_date_option.delete()
            vote.delete()
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.data_delete, 'VO-C-006', request)  # ------------------------------------------006

        try:
            GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid, trigger_type='D',
                                    do_type_id=5, old=str(title))
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.log_create, 'VO-C-007', request)  # ------------------------------------------007
        return success(request=request)

    # /vote/get/  -----------------------------------------------------------------------------------------------------D
    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data['uid']
        vote_no = data['voteNum']

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-D-001', request)  # -----------------------------------------------001

        try:
            GroupMember.objects.get(group_no=vote.group_no, user_id=uid, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'VO-D-002', request)  # -----------------------------------------002

        try:
            vote_option = VoteDateOption.objects.filter(
                vote_no=vote) if vote.option_type_id == 2 else VoteOption.objects.filter(vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.option_read, 'VO-D-003', request)  # ------------------------------------------003

        try:
            vote_record = VoteRecord.objects.filter(vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.record_read, 'VO-D-004', request)  # ------------------------------------------004

        vote_option_list = []
        for i in vote_option:
            vote_count = VoteRecord.objects.filter(vote_no=vote_no, option_num=i.option_num).count()
            is_vote = True if VoteRecord.objects.filter(vote_no=vote_no, option_num=i.option_num,
                                                        user_id=uid).count() > 0 else False
            vote_option_list.append(
                {
                    'voteItemNum': int(i.option_num),
                    'voteItemName': str(i.content),
                    'voteItemCount': int(vote_count),
                    'isVote': is_vote
                }
            )
        response = {
            'title': vote.title,
            'founderId': vote.founder_id,
            'founderName': Account.objects.get(user_id=vote.founder.user_id).name,
            'optionTypeId': vote.option_type_id,
            'voteItems': vote_option_list,
            'addItemPermit': bool(vote.is_add_option),
            'deadline': str(vote.end_time),
            'anonymous': bool(vote.is_anonymous),
            'chooseVoteQuantity': vote.multiple_choice,
            'voteCount': vote_record.count()
        }
        return success(response, request)

    # /vote/get_list/  ------------------------------------------------------------------------------------------------E
    @action(detail=False)
    def get_list(self, request):
        data = request.query_params

        uid = data['uid']
        group_no = data['groupNum']

        try:
            GroupMember.objects.get(group_no=group_no, user_id=uid, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'VO-E-001', request)  # -----------------------------------------001

        try:
            vote = Vote.objects.filter(group_no=group_no)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-E-002', request)  # -----------------------------------------------002

        vote_list = []
        now = datetime.now()
        for i in vote:
            end_time = i.end_time if i.end_time is not None else now
            if end_time >= now or i.end_time is None:
                try:
                    vote_record = VoteRecord.objects.filter(vote_no=i.serial_no)
                except:
                    return err(Msg.Err.Vote.record_read, 'VO-E-003', request)  # ----------------------------------003
                try:
                    is_vote = True if VoteRecord.objects.filter(vote_no=i.serial_no, user_id=uid).count() > 0 else False
                except:
                    return err(Msg.Err.Vote.record_read, 'VO-E-004', request)  # ----------------------------------004
                vote_list.append(
                    {
                        'voteNum': i.serial_no,
                        'votersNum': vote_record.values('user_id').annotate(Count('user_id')).count(),
                        'title': i.title,
                        'isVoteType': is_vote
                    }
                )

        response = {'vote': vote_list}
        return success(response, request)

    # /vote/vote/  ----------------------------------------------------------------------------------------------------F
    @action(detail=False, methods=['POST'])
    def vote(self, request):
        data = request.data

        uid = data['uid']
        vote_no = data['voteNum']
        vote_option_no = data['voteItemNum']

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-F-001', request)  # -----------------------------------------------001

        if vote.end_time < datetime.now():
            return vote_expired(request)
        if len(vote_option_no) > vote.multiple_choice:
            return limit_vote(request)

        try:
            GroupMember.objects.get(user_id=uid, group_no=vote.group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'VO-F-002', request)  # -----------------------------------------002

        try:
            vote_record = VoteRecord.objects.filter(user_id=uid, vote_no=vote)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.record_read, 'VO-F-003', request)  # ------------------------------------------003

        record_list = []
        for i in vote_record:
            record_list.append(i.option_num)
            if i.option_num not in vote_option_no:
                try:
                    VoteRecord.objects.filter(user_id=uid, vote_no=vote, option_num=i.option_num).delete()
                except:
                    return err(Msg.Err.Vote.record_read, 'VO-F-004', request)  # ----------------------------------004

        for i in vote_option_no:
            if i not in record_list:
                try:
                    VoteRecord.objects.create(vote_no=vote, option_num=i, user_id=uid, vote_time=datetime.now())
                except:
                    return err(Msg.Err.Vote.record_create, 'VO-F-005', request)  # --------------------------------005

        return success(request=request)

    # /vote/add_items/  -----------------------------------------------------------------------------------------------G
    @action(detail=False, methods=['POST'])
    def add_items(self, request):
        data = request.data

        uid = data['uid']
        vote_no = data['voteNum']
        vote_items = data['voteItems']

        try:
            vote = Vote.objects.get(serial_no=vote_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.vote, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-G-001', request)  # -----------------------------------------------001

        if vote.end_time < datetime.now():
            return vote_expired(request)
        title = vote.title
        group_no = vote.group_no
        try:
            GroupMember.objects.get(user_id=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'VO-G-002', request)  # -----------------------------------------002

        vote_option = VoteDateOption if vote.option_type_id == 2 else VoteOption
        exist_no_list = []
        exist_content_list = []
        for i in vote_items:
            option_no = i['voteItemNum']
            content = i['voteItemName']
            try:
                vote_option.objects.get(vote_no=vote, option_num=option_no)
                exist_no_list.append(option_no)
                exist_content_list.append(content)
            except ObjectDoesNotExist:
                vote_option.objects.create(vote_no=vote, option_num=option_no, content=content)
        if len(exist_no_list) > 0:
            return vote_option_exist(f'{str(exist_no_list)}內容為{str(exist_content_list)}', request)

        try:
            GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid, trigger_type='I',
                                    do_type_id=6, new=title)
        except Exception as e:
            print(e)
            err(Msg.Err.Group.log_create, 'VO-G-003', request)  # -------------------------------------------------003

        return success(request=request)

    # /vote/get_end_list/  --------------------------------------------------------------------------------------------H
    @action(detail=False)
    def get_end_list(self, request):
        data = request.query_params

        uid = data['uid']
        group_no = data['groupNum']

        try:
            GroupMember.objects.get(user_id=uid, group_no=group_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'VO-H-001', request)  # -----------------------------------------001

        try:
            vote = Vote.objects.filter(group_no=group_no)
        except Exception as e:
            print(e)
            return err(Msg.Err.Vote.select, 'VO-H-002', request)  # -----------------------------------------------002

        vote_list = []
        now = datetime.now()
        for i in vote:
            end_time = i.end_time if i.end_time is not None else now
            if end_time < datetime.now():
                vote_no = i.serial_no
                vote_option = VoteDateOption if i.option_type_id == 2 else VoteOption

                try:
                    vote_record = VoteRecord.objects.filter(vote_no=vote_no).values('option_num').annotate(
                        count=Count('user_id'))
                    result_count = vote_record.filter().aggregate(vote_count=Max('count'))['vote_count']
                    result_data = vote_record.filter(count=result_count)
                except:
                    return err(Msg.Err.Vote.record_read, 'VO-H-003', request)  # ----------------------------------003

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
                        return not_found(Msg.NotFound.vote_option, request)
                    except:
                        return err(Msg.Err.Vote.select, 'VO-H-004', request)  # -----------------------------------004

                vote_list.append(
                    {
                        'voteNum': i.serial_no,
                        'title': i.title,
                        'result': result,
                        'resultCount': result_count
                    }
                )
        response = {'vote': vote_list}
        return success(response, request)
