// Leap_MotionC++.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"

#include <iostream>
#include <cstring>
#include <Windows.h>
#include "Leap.h"
using namespace Leap;

Controller controller;

float buffer[3];
unsigned char *leap_buffer;
/*

HandList hands;
  hands = f.hands();

  for (HandList::const_iterator hl = hands.begin(); hl != hands.end(); ++hl){
    Hand hand = *hl;
    if(hand.isRight()){
      right_hand = true;
      x = (int)hand.palmPosition().x;
      z = (int)hand.palmPosition().z;
      old_palm_normal = palm_normal;
      if(hand.palmNormal().y > 0)
        palm_normal = 1;
      else
        palm_normal = 0;
    }
  }
  if(hands.isEmpty()) right_hand = false;

*/

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

	if (hMapFile == NULL)
		{
		printf("Could not create file mapping object.\n");
		return NULL;
		}

	return (unsigned char*)MapViewOfFile(hMapFile,   // handle to map object
		FILE_MAP_ALL_ACCESS, // read/write permission
		0,
		0,
		buf_size);

	}

void read_frame() 
{
	float x = 0, z = 0, y = 0;
	Frame f = controller.frame();
	HandList hands;
    hands = f.hands();
	
	for (HandList::const_iterator hl = hands.begin(); hl != hands.end(); ++hl) {
		Hand hand = *hl;
		//if (hand.isRight()) {
			buffer[0] = hand.palmPosition().x;
			buffer[1] = hand.palmPosition().y;
			buffer[2] = hand.palmPosition().z;
			memcpy((void *)leap_buffer, (void *)buffer, 12);
			//z = hand.palmPosition().z;
			std::cout << buffer[0] <<" "<< buffer[1] <<" "<< buffer[2]<< std::endl;
		//}
	}
	
	//printf("Timestamp %ud, x: %f, y:%f\n", f.timestamp(), x, y);
}


int _tmain(int argc, _TCHAR* argv[])
{	
	controller.setPolicy(Leap::Controller::POLICY_BACKGROUND_FRAMES);
   leap_buffer = OpenSharedMemoryBuffer("LeapBuffer" , 12);
  //controller.setPolicy(Leap::Controller::POLICY_ALLOW_PAUSE_RESUME);

  while (true) {
	read_frame();
	Sleep(100);
  }

   return 0;
}

