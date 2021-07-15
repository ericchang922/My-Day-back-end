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
        # schedule
        schedule = '行程不存在'
        personal_schedule = '用戶沒有此行程'
        no_personal_schedule = '用戶沒有行程'
        common_schedule = '共同行程不存在'
        schedule_notice = '提醒不存在'
        # note
        note = '筆記不存在'
        user_note = '用戶沒有此筆記'
        # vote
        vote = '沒有此投票'
        user_vote = '用戶沒有此投票'
        # group
        group = '群組不存在'
        not_in_group = '用戶沒有此群組'
