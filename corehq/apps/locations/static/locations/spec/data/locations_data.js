hqDefine('locations/spec/data/locations_data.js', function(){
    return {
        state:{
            "view_descendants":false,
            "code":"state",
            "expand_from":null,
            "name":"state",
            "expand_from_root":false,
            "pk":1,
            "expand_to":null,
            "parent_type":null,
            "shares_cases":true,
            "administrative":true,
        },

        district:{
            "view_descendants":false,
            "code":"district",
            "expand_from":null,
            "name":"district",
            "expand_from_root":false,
            "pk":2,
            "expand_to":null,
            "parent_type":1,
            "shares_cases":true,
            "administrative":true,
        },

        block:{
            "view_descendants":false,
            "code":"block",
            "expand_from":null,
            "name":"block",
            "expand_from_root":false,
            "pk":3,
            "expand_to":null,
            "parent_type":2,
            "shares_cases":true,
            "administrative":true,
        },

        supervisor: {
            "view_descendants":false,
            "code":"supervisor",
            "expand_from":null,
            "name":"supervisor",
            "expand_from_root":false,
            "pk":4,
            "expand_to":null,
            "parent_type":3,
            "shares_cases":true,
            "administrative":true,
        },
    };
});
