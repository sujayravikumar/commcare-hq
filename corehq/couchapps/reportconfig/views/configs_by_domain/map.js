function (doc) {
    if (doc.doc_type == "ReportConfig") {
        emit(["owned", doc.domain, doc.owner_id, doc.report_slug], null);

        if (doc.sharing) {
            var i,
                shared_with = doc.sharing.shared_with;
            for(i = 0; i < shared_with.length; i++) {
                emit(["shared", doc.domain, shared_with[i].target, doc.report_slug], null);
            }
        }
    }
}