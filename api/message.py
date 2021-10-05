class Msg:
    class Err:
        class Timetable:
            create_create = '建立課表錯誤'
            school_create = '建立學校錯誤'
            personal_create = '建立個人課表錯誤'
            section_create = '建立節次錯誤'
            subject_create = '建立科目錯誤'
            create = '建立課表內容錯誤'
            time_create = '建立節次時間錯誤'
            update = '更新課表內容錯誤'
            information_update = '更新課表資訊錯誤'
            section_update = '更新節次錯誤'
            get_school = '取得學校錯誤'
            get_classtime = '取得課程錯誤'
            get_time = '取得節次錯誤'
            get_timetable = '取得課表錯誤'
            get_timetable_list = '取得課表列表錯誤'
            get_sharecode = '分享碼錯誤'


        class Account:
            get = '取得帳號錯誤'
            registered = '此email已被使用'
            account_create = '建立帳號錯誤'
            login = '登入失敗'
            verification_code = '驗證碼錯誤'

        class Schedule:
            create = '建立行程錯誤'
            select = '查詢行程錯誤'
            # personal_schedule
            personal_create = '建立個人行程錯誤'
            personal_delete = '個人行程刪除錯誤'
            personal_select = '個人行程查詢錯誤'
            # schedule_notice
            notice_create = '建立提醒錯誤'
            notice_delete = '提醒刪除錯誤'

        class Note:
            create = '建立筆記錯誤'
            select = '查詢筆記錯誤'
            delete = '刪除筆記錯誤'

        class Vote:
            create = '建立投票錯誤'
            select = '查詢投票錯誤'
            data_delete = '行程資料刪除錯誤'
            # vote_option
            option_create = '建立投票項目錯誤'
            option_read = '一般投票選項讀取錯誤'
            option_err = '投票項目可能因為發生錯誤而消失，請重新新增選項'
            date_option_read = '日期投票選項讀取錯誤'
            # vote_record
            record_create = '建立投票紀錄錯誤'
            record_read = '讀取投票紀錄錯誤'
            # type
            type = ['錯誤', '錯誤：請傳入文字', '錯誤：請傳入日期']

        class Group:
            select = '查詢群組錯誤'
            time = '時間設定錯誤'
            # group_member
            at_least_one_friend = '至少一位好友'
            member_read = '群組資料讀取錯誤'
            friend_only = '僅能邀請好友'
            already_invited = '已邀請'
            only_one_manager = '您是唯一管理者，需先指定另一位管理者才能退出'
            already_joined = '已加入群組'
            must_choose_others = '需選擇其他成員'
            # group_log
            log_create = '新增群組紀錄錯誤'

        class Friend:
            already_sent_request = '已送出邀請'
            already_best_friend = '已為摯友'

        class StudyPlan:
            at_least_one_subject = '至少要有一個科目'
            already_existed = '此行程已有讀書計畫'
            not_study_plan_schedule = '行程非讀書計畫行程'
            only_share_with_one_group = '僅能分享一個群組'
            has_been_shared = '已分享過給此群組'
            has_been_canceled = '已取消分享'
            already_studied = '已與群組一起讀過'
            disconnect_group_first = '請先取消分享讀書計畫'
            select_old = '請選擇尚未開始的讀書計畫'

    class NotFound:
        type = ''
        # account
        account = '查無使用者'
        verification_code = '查無驗證碼'

        # timetable
        timetable = '課表不存在'
        personal_timetable = '用戶沒有此課表'
        class_time = '沒有課程時間'
        section = '沒有節次'
        subject = '沒有科目'
        school = '不存在的學校'
        share_log = '查無分享紀錄'

        # friend
        friend = '無此好友'
        best_friend = '無此摯友'
        relation = '不存在的關係代碼'
        friend_request = '沒有邀請關係'

        # group
        group = '群組不存在'
        not_in_group = '用戶沒有此群組'  # group_member
        member_status = '不存在的狀態碼'
        group_log = '群組沒有紀錄'
        do_type = '不存在的行為類別'
        user_has_left = '已退出群組'
        member = '無此成員'
        group_invite = '沒有此群組的邀請'

        # note
        note = '筆記不存在'
        user_note = '用戶沒有此筆記'
        note_not_share = '此筆記沒有被分享，無法取消分享'
        note_is_share = '此筆記原本已分享'

        # setting
        notice = '找不到通知設定'
        theme = '找不到的主題'

        # vote
        vote = '沒有此投票'
        user_vote = '用戶沒有此投票'
        vote_option = '沒有此選項'
        option_type = '不存在的投票類別'
        vote_record = '沒有投票紀錄'

        # schedule
        schedule = '行程不存在'
        personal_schedule = '用戶沒有此行程'
        no_personal_schedule = '用戶沒有行程'
        common_schedule = '共同行程不存在'
        schedule_notice = '提醒不存在'

        # study_plan
        study_plan = '讀書計畫不存在'
        plan_content = '讀書計畫沒有此內容'
