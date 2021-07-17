class Msg:
    class Err:
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
            # group_member
            member_read = '群組資料讀取錯誤'

    class NotFound:
        type = ''
        # account
        account = '查無使用者'
        verification_code = '驗證碼不正確'

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
        relation = '不存在的關係代碼'

        # group
        group = '群組不存在'
        not_in_group = '用戶沒有此群組'  # group_member
        member_status = '不存在的狀態碼'
        group_log = '群組沒有紀錄'
        do_type = '不存在的行為類別'

        # note
        note = '筆記不存在'
        user_note = '用戶沒有此筆記'

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
        study_plan = '學習計畫不存在'
        plan_content = '學習計畫沒有此內容'
