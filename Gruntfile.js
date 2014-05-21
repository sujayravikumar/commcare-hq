module.exports = function (grunt) {

  var appConfig = grunt.file.readJSON('package.json');

  // Load grunt tasks automatically
  // see: https://github.com/sindresorhus/load-grunt-tasks
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  // see: https://npmjs.org/package/time-grunt
  require('time-grunt')(grunt);
  
  //  https://github.com/gruntjs/grunt-contrib-less
  grunt.loadNpmTasks('grunt-contrib-less');

  var pathsConfig = function (appName) {
    this.app = appName || appConfig.name;

    return {
      app: this.app,
      css: './submodules/hqstyle-src/hqstyle/static/hqstyle/css/core/',
      less: './submodules/hqstyle-src/hqstyle/_less/core/',
      manageScript: './manage.py'
    };
  };

  grunt.initConfig({

    paths: pathsConfig(),
    pkg: appConfig,

    // see: https://github.com/gruntjs/grunt-contrib-watch
    watch: {
      gruntfile: {
        files: ['Gruntfile.js']
      },
      less: {
        files: ['<%= paths.less %>/**/*.less'],
        tasks: ['less:development']
      },
    },

    //  see:  https://github.com/gruntjs/grunt-contrib-less
    less: {
      development: {
        options: {
          paths: ['<%= paths.less %>'],
          compress: false,
          strictImports: true,
        },
        files: {
          "<%= paths.css %>hqstyle-core.css":  
          "<%= paths.less %>hqstyle-core.less"
        }
      },
      production: {
        // TODO 
      },
    },

    // see: https://npmjs.org/package/grunt-bg-shell
    bgShell: {
      _defaults: {
        bg: true
      },
      runDjango: {
        cmd: 'python <%= paths.manageScript %> runserver'
      }
    }
  });

  grunt.registerTask('serve', [
    'bgShell:runDjango',
    'watch'
  ]);

  grunt.registerTask('makeLess', [
    'less:development',
  ]);

  grunt.registerTask('default', [
    'serve'
  ]);
};

