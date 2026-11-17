<template>
  <div id="header" >
      <div id="header-left">
          <h1>医疗疾病数据分析大屏可视化系统</h1>
      </div>
      <div id="header-nav">
            <div  :class="['header-nav-item',activePath == item.path ? 'active' : '','cool-border']" @click="routerChange(item.path)" v-for="item in routerLink">
                    <router-link class="nav content" :to="item.path">
                        {{item.meta.name}}
                    </router-link>
                    <div :class="[activePath == item.path ? 'top-left' : '','corner']" ></div>
                    <div :class="[activePath == item.path ? 'top-right' : '','corner']"></div>
                    <div :class="[activePath == item.path ? 'bottom-left' : '','corner']"></div>
                    <div :class="[activePath == item.path ? 'bottom-right' : '','corner']"></div>
            </div>
            
      </div>
      <div id="header-time">
          {{ currentDateTime }}
      </div>
  </div>
</template>

<script>
export default {
    data(){
        return {
            activePath:"/",
            routerLink:[],
            currentDateTime: this.getCurrentDateTime()
        }
    },
    created(){
        this.routerLink = this.$router.options.routes;
        this.activePath = this.$route.path
        this.interval = setInterval(() => {
            this.currentDateTime = this.getCurrentDateTime();
        }, 1000);
    },
    watch: {
        // 浏览器前进/后退、直接在地址栏切换路由时也同步导航高亮
        '$route'(to) {
            this.activePath = to.path;
        }
    },
    beforeDestroy() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    },
    methods:{
        getCurrentDateTime() {
            const now = new Date();
            const year = now.getFullYear();
            const month = (now.getMonth() + 1).toString().padStart(2, '0');
            const day = now.getDate().toString().padStart(2, '0');
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        },
        routerChange(path){
            this.activePath = path
        }
    }
}
</script>

<style lang="less" scoped>
        #header-time{
            color:#52a2e4;
            font-size: 17px;
        }
        .cool-border {
            position: relative;
        }
        
        .corner {
            position: absolute;
            width: 0;
            height: 0;
            border: 5px solid transparent;
        }
        
        .top-left {
            top: 0;
            left: 0;
            border-top-color: #fff;
            border-left-color: #fff;
        }
        .top-right {
            top: 0;
            right: 0;
            border-top-color: #fff;
            border-right-color: #fff;
        }
        .bottom-left {
            bottom: 0;
            left: 0;
            border-bottom-color: #fff;
            border-left-color: #fff;
        }
        .bottom-right {
            bottom: 0;
            right: 0;
            border-bottom-color: #fff;
            border-right-color: #fff;
        }
        
        .content {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    #header{
        display: flex;
        padding: 10px 150px 0 150px;
        align-items: center;
        justify-content: space-between;
        #header-left{
            flex-shrink: 0;
            h1{
                color:#fff;
                font-size: 23px;
                white-space: nowrap;
            }
        }
        #header-nav{
            display: flex;
            flex-shrink: 0;
            .header-nav-item{
                margin-right: 15px;
                padding:10px 40px;
                border: 1px solid transparent;
                border-radius: 80px;
                white-space: nowrap;
            }
            .header-nav-item.active{
                background: #1b2d4a;
            }
            .nav{
                text-decoration: none;
                color:#52a2e4;
                font-size: 15px;
                white-space: nowrap;
            }
        }
        #header-time{
            flex-shrink: 0;
            white-space: nowrap;
        }
        // #header-time{
        //     font-size: 17px;
        // }
    }

    @media (max-width: 1700px) {
        #header {
            padding: 10px 30px 0 30px;

            #header-left h1 {
                font-size: 20px;
            }

            #header-nav .header-nav-item {
                margin-right: 8px;
                padding: 9px 22px;
            }

            #header-time {
                font-size: 14px;
            }
        }
    }

    @media (max-width: 1366px) {
        #header {
            padding: 8px 16px 0 16px;

            #header-left h1 {
                font-size: 17px;
            }

            #header-nav .header-nav-item {
                margin-right: 4px;
                padding: 8px 12px;
            }

            #header-nav .nav {
                font-size: 13px;
            }

            #header-time {
                font-size: 12px;
            }
        }
    }
</style>