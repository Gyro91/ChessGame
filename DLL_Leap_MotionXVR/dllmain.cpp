// dllmain.cpp : Defines the entry point for the DLL application.
#include "stdafx.h"

#include <windows.h>
#include <stdio.h>
#include <iostream> 
#include <vector> 
#include <string> 
using namespace std;

#define SIZE_BUFF 163


float x[SIZE_BUFF];
unsigned char* mybuffer;

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

unsigned char *OpenSharedMemoryBuffer(char *name,int buf_size)
{

	//Apre un nmemory buffer. Se non esiste lo crea.
	HANDLE hMapFile;

	hMapFile = CreateFileMapping(
		INVALID_HANDLE_VALUE,    // use paging file
		NULL,                    // default security
		PAGE_READWRITE,          // read/write access
		0,                       // maximum object size (high-order DWORD)
		buf_size,                // maximum object size (low-order DWORD)
		name);                 // name of mapping object

	if (hMapFile == NULL) {
		printf("Could not create file mapping object.\n");
		return NULL;
	}

	return (unsigned char*)MapViewOfFile(hMapFile,   // handle to map object
		FILE_MAP_ALL_ACCESS, // read/write permission
		0,
		0,
		buf_size);

}


extern "C" __declspec(dllexport) char * __XVR_INIT (void *XVR_pointer)
{
	//New feature from 0141. This function is optional. If you declare it XVR will execute it after loading the DLL
	//You can use it to do initialisation code, as well as to get internal parameters from the XVR virtual machine	
	
	mybuffer = OpenSharedMemoryBuffer("LeapBuffer", 48);

	return(NULL); 
} 

extern "C" __declspec(dllexport) void get_seq_number(float* out)
{	
	memcpy(out, &mybuffer[0], 4);
}

/*
*	ottimizzo dicendo che y del palmo è sempre maggiore di 0
*	la funzione restituisce 1 se la mano è assente
*/
extern "C" __declspec(dllexport) int get_right_hand(float* out)
{	
	float test;
	
	memcpy(&test, &mybuffer[(2*4)], 4);
	
	if (test == 0) 
		return 1;
	
	memcpy(out, &mybuffer[1*4], 324);
	
	return 0;
}

extern "C" __declspec(dllexport) int get_left_hand(float* out)
{	
	float test;
	
	memcpy(&test, &mybuffer[(83*4)], 4);
	
	if (test == 0) 
		return 1;
	
	memcpy(out, &mybuffer[82*4], 324);
	
	return 0;
}