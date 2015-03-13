function (doc) {
    if (doc.doc_type == "ReportConfig") {
        emit(["owned", doc.domain, doc.owner_id, doc.report_slug], null);

        if (doc.sharing) {
            for(target in doc.sharing.shared_with) {
                emit(["shared", doc.domain, target, doc.report_slug], null);
            }

            var i,
                excluded = doc.sharing.excluded_users;
            if (excluded) {
                for (i = 0; i < excluded.length; i++) {
                    emit(["excluded", doc.domain, excluded[i], doc.report_slug], null);
                }
            }
        }
    }
}