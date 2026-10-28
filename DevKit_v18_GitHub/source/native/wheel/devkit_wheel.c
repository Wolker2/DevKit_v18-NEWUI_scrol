/* DevKit wheel adapter v1.0: a hook on the invoking UI thread only.
 * Script exports use cdecl; Windows callbacks/imports use stdcall.
 * No game addresses, game memory access, timers, threads or background polling.
 */
#ifdef WHEEL_TEST
#define WIN
#else
#define WIN __attribute__((stdcall))
#endif
typedef unsigned int U32;
typedef __INTPTR_TYPE__ IPTR;
typedef __UINTPTR_TYPE__ UPTR;
typedef void *HANDLE;
typedef struct { int x,y; } POINT;
typedef struct { HANDLE hwnd;U32 message;UPTR wParam;IPTR lParam;U32 time;POINT pt; } MSG;
typedef IPTR (WIN *HOOKPROC)(int,UPTR,IPTR);
extern U32 WIN GetCurrentThreadId(void);
extern HANDLE WIN GetForegroundWindow(void);
extern U32 WIN GetWindowThreadProcessId(HANDLE,U32*);
extern int WIN ScreenToClient(HANDLE,POINT*);
extern HANDLE WIN SetWindowsHookExW(int,HOOKPROC,HANDLE,U32);
extern int WIN UnhookWindowsHookEx(HANDLE);
extern IPTR WIN CallNextHookEx(HANDLE,int,UPTR,IPTR);
extern int WIN PostMessageW(HANDLE,U32,UPTR,IPTR);

#ifndef WHEEL_TEST
_Static_assert(sizeof(void*)==4,"32-bit game module required");
_Static_assert(sizeof(MSG)==28,"Win32 MSG layout mismatch");
#endif
static HANDLE self_module,hook,game_window;
static int left_edge,top_edge,right_edge,bottom_edge,remainder;
enum { WM_NULL=0,WM_KEYDOWN=0x100,WM_MOUSEWHEEL=0x20a,PGUP=33,PGDN=34 };

static IPTR WIN WheelMessage(int ncode,UPTR removed,IPTR message_ptr){
    MSG *msg=(MSG*)message_ptr;
    if(ncode==0 && removed==1 && hook && msg && msg->message==WM_MOUSEWHEEL &&
       msg->hwnd==game_window && GetForegroundWindow()==game_window){
        POINT p={(short)(msg->lParam&65535),(short)(((UPTR)msg->lParam>>16)&65535)};
        if(ScreenToClient(game_window,&p) && p.x>=left_edge && p.x<right_edge &&
           p.y>=top_edge && p.y<bottom_edge){
            int delta=(short)(msg->wParam>>16);
            int steps,key,count;
            remainder+=delta;
            steps=remainder/120;
            remainder-=steps*120;
            /* A partial wheel tick is consumed; it must not reach the game. */
            if(!steps){msg->message=WM_NULL;msg->wParam=0;msg->lParam=0;}
            else{
                key=steps>0?PGUP:PGDN;
                count=steps>0?steps:-steps;
                msg->message=WM_KEYDOWN;msg->wParam=(UPTR)key;msg->lParam=1;
                /* A single removed message produces each notch exactly once. */
                while(--count>0) PostMessageW(game_window,WM_KEYDOWN,(UPTR)key,1);
            }
        }else remainder=0;
    }
    return CallNextHookEx(hook,ncode,removed,message_ptr);
}

int WheelDisable(void){
    HANDLE previous=hook;
    if(previous && !UnhookWindowsHookEx(previous))return 0;
    hook=0;game_window=0;remainder=0;
    return 1;
}

int WheelEnable(int x1,int y1,int x2,int y2){
    HANDLE window=GetForegroundWindow();
    U32 thread=GetCurrentThreadId();
    if(!window || !thread || GetWindowThreadProcessId(window,0)!=thread || x2<=x1 || y2<=y1)return 0;
    if(hook && !WheelDisable())return 0;
    game_window=window;left_edge=x1;top_edge=y1;right_edge=x2;bottom_edge=y2;remainder=0;
    hook=SetWindowsHookExW(3,WheelMessage,self_module,thread);
    if(!hook){game_window=0;return 0;}
    return 1;
}

int WIN DllMain(HANDLE module,U32 reason,void *reserved){
    (void)reserved;
    if(reason==1)self_module=module;
    else if(reason==0 && hook)WheelDisable();
    return 1;
}
