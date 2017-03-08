// dllmain.cpp : Defines the entry point for the DLL application.
#include "stdafx.h"

#include <windows.h>
#include <stdio.h>
#include <iostream> 
#include <vector> 
#include <string> 
using namespace std;
#define GLEW_STATIC 
#include "glew/glew.h"
#include "glew/wglew.h"
#include "glew/glsl.h"


#pragma comment(lib,"opengl32.lib")
#pragma comment(lib,"glu32.lib")
#pragma comment(lib,"glew/glew32s.lib")

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}


void draw_textured_quad(float x1, float y1, float x2, float y2)
{
	glBegin(GL_QUADS);
	glTexCoord2f(1,0);
	glVertex3f(x2,y2,0);
	glTexCoord2f(0,0);
	glVertex3f(x1,y2,0);
	glTexCoord2f(0,1);
	glVertex3f(x1,y1,0);
	glTexCoord2f(1,1);
	glVertex3f(x2,y1,0);
	glEnd();	
}

extern "C" __declspec(dllexport) void init_leap_motion()
{	
	
	
		for(int i= 0; i<36 ; i++)
		{
			draw_textured_quad(-1,-1,1,1);
			glTranslatef(2,0,0);
			glRotatef(10,0,1,0);	
		}
}