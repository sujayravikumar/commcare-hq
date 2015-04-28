function(doc) {
    if (doc.doc_type === 'BlanketRequestDocument') {
        emit([doc.view_name, doc.path], doc.time_taken);
    }
}
