from hook.base import BaseHook
from task.markemedia.tasks import send2markemedia
from common.utils import oceanus_logging

logger = oceanus_logging()


class NamecardHook(BaseHook):

    def main(self) -> int:
        channel = self.item.get("channel")
        if channel != "namecard":
            return 0

        data = self.item.get("data")
        if data.get("oid").startswith("mm_") is False:
            return 0

        jsn = self.item.get("jsn")
        if len(jsn) == 0:
            return 0

        count = 1
        form_data = {
            "documents": {
                "document_id":     jsn.get("document_id", ""),
                "req_detail_info": jsn.get("req_detail_info", ""),
                "document_anq":    jsn.get("document_anq", "")
            },
            "c_type":        jsn.get("c_type", ""),
            "company_name": data.get("cname", ""),
            "url":           jsn.get("url", ""),
            "name":         data.get("name", ""),
            "division":      jsn.get("department", ""),
            "post_name":     jsn.get("post_name", ""),
            "zip1":          jsn.get("zip01", ""),
            "zip2":          jsn.get("zip02", ""),
            "address1":      jsn.get("prefecture", ""),
            "address2": '{0} {1}'.format(jsn.get("address", ""),
                                         jsn.get("addressDetail", "")),
            "tel1":          jsn.get("tel1", ""),
            "tel2":          jsn.get("tel2", ""),
            "tel3":          jsn.get("tel3", ""),
            "email":        data.get("email", ""),
            "business":      jsn.get("business", ""),
            "post":          jsn.get("post", ""),
            "occupational":  jsn.get("occupational", ""),
            "employees":     jsn.get("employees", ""),
            "turnover":      jsn.get("turnover", ""),
            "anq":           jsn.get("anq", ""),
            "anq2":          jsn.get("anq2", ""),
        }
        logger.info("form_data:{}".format(form_data))

        send2markemedia.delay(form_data=form_data)

        return count
