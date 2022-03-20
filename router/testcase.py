"""
__author__ = '霍格沃兹测试开发学社'
__desc__ = '更多测试开发技术探讨，请访问：https://ceshiren.com/t/topic/15860'
"""
from flask import request
from flask_restx import Namespace, Resource

from backend_actual.log_util import logger
from dao.testcase_model import TestCase
from server import api, db

case_ns = Namespace("case", description="用例管理")

@case_ns.route("")
class TestCaseServer(Resource):
    get_paresr = api.parser()
    # 查询接口， 可以传id ，也可以不传id，
    # 不传id：就是返回 全部记录
    # 传id：返回查询到的对应的记录，如果未查到则返回 空列表
    get_paresr.add_argument("id", type=int, location="args")

    @case_ns.expect(get_paresr)
    def get(self):
        """
        测试用例的查找
        :return:
        """
        case_id = request.args.get("id")

        logger.info(f"type(request.args) <===== {type(request.args)}")
        logger.info(f"接收到的参数 <===== {case_id}")
        if case_id:
            # 如果不为空，查询操作
            case_data = TestCase.query.filter_by(id=case_id).first()
            logger.info(f"{case_data}")
            if case_data:
                datas = [{"id": case_data.id,
                          "case_title": case_data.case_title,
                          "remark": case_data.remark}]
                logger.info(f"要返回的数据为<======{datas}")
            else:
                datas = []
        else:
            # 为空，返回所有记录
            case_datas = TestCase.query.all()
            datas = [{"id": case_data.id,
                      "case_title": case_data.case_title,
                      "remark": case_data.remark} for case_data in case_datas]

        return datas

    post_paresr = api.parser()
    post_paresr.add_argument("id", type=int, required=True, location="json")
    post_paresr.add_argument("case_title", type=str, required=True, location="json")
    post_paresr.add_argument("remark", type=str, location="json")

    @case_ns.expect(post_paresr)
    def post(self):
        """
        测试用例的新增
        :return:
        """
        # 获取请求数据
        case_data = request.json
        logger.info(f"接收到的参数<====== {case_data}")
        case_id = case_data.get("id")
        # 查询数据库，查看是否有记录
        exists = TestCase.query.filter_by(id=case_id).first()
        logger.info(f"查询表结果：{exists}")
        # 如果不存在，则添加这条记录到库中
        # 如果存在，不执行新增操作， 返回 40001错误码
        if not exists:
            testcase = TestCase(**case_data)
            logger.info(f"将要存储的内容为<======{testcase}")
            db.session.add(testcase)
            db.session.commit()
            db.session.close()
            return {"code": 0, "msg": f"case id {case_id} success add."}
        else:
            return {"code": 40001, "msg": "case is exists"}

    put_paresr = api.parser()
    put_paresr.add_argument("id", type=int, required=True, location="json")
    put_paresr.add_argument("case_title", type=str, required=True, location="json")
    put_paresr.add_argument("remark", type=str, location="json")

    @case_ns.expect(put_paresr)
    def put(self):
        """
        测试用例的修改
        :return:
        """
        case_data = request.json
        logger.info(f"接收到的参数<====== {case_data}")
        case_id = case_data.get("id")
        # 查询数据库，查看是否有记录
        exists = TestCase.query.filter_by(id=case_id).first()
        logger.info(f"查询表结果：{exists}")
        # 如果不存在，则 不执行修改操作 并返回 40002
        # 如果存在，执行修改操作
        if exists:
            case_data1 = {}
            case_data1["case_title"] = case_data.get("case_title")
            case_data1["remark"] = case_data.get("remark")
            TestCase.query.filter_by(id=case_id).update(case_data1)
            db.session.commit()
            db.session.close()
            return {"code": 0, "msg": f"case id {case_id} success change to {case_data1}"}
        else:
            return {"code": 40002, "msg": "case is not exists"}

    delete_parser = api.parser()
    delete_parser.add_argument("id", type=int, location="json", required=True)

    @case_ns.expect(delete_parser)
    def delete(self):
        """
        测试用例的删除
        :return:
        """
        case_data = request.json
        case_id = case_data.get("id")
        logger.info(f"接收到的参数id <====={case_id}")
        exists = TestCase.query.filter_by(id=case_id).first()
        if exists:
            TestCase.query.filter_by(id=case_id).delete()
            # commit 之后需要添加close
            db.session.commit()
            db.session.close()

            return {"code": 0, "msg": f"case id {case_id} success delete"}
        else:
            return {"code": 40002, "msg": f"case is not exists"}
