#include "Logger.h"
#include <Windows.h>
#include <stdlib.h>

namespace Logger
{
void Log( const std::string& f, int n, const std::string& str ) 
{
	printf( "%s (%d):%s\n",f.c_str(), n, str.c_str() );
}

void Log( const std::string& f, int n, const std::wstring& str )
{
	std::string strToWrite;
	strToWrite.resize( str.size() );
	WideCharToMultiByte( CP_ACP, 0, &str[0], -1, &strToWrite[0], (int)str.size(), NULL, NULL );
	Log( f,n,strToWrite );
}
}