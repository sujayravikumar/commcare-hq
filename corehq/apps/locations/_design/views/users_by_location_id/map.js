function(doc) {
    if ((doc.doc_type == "WebUser" || doc.doc_type == "CommCareUser") && doc.location_id) {
        emit([doc.location_id, doc.doc_type, doc._id], null);
    }
}
