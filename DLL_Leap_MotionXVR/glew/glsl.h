// GL ERROR CHECK
#define CHECK_GL_ERROR() CheckGLError(__FILE__, __LINE__)
// GL ERROR CHECK
int CheckGLError(char *file, int line)
{
	//return 0;
	GLenum glErr,glErr2;
	int retCode = 0;

	glErr = glErr2 = glGetError();
	while (glErr != GL_NO_ERROR) 
	{
	   char* str1 = (char*)gluErrorString(glErr);
	   if (str1)
			cout << "GL Error #" << glErr << "(" << str1 << ") " << " in File " << file << " at line: " << line << endl;
	   else
			cout << "GL Error #" << glErr << " in File " << file << " at line: " << line << endl;
		retCode = 1;
		glErr = glGetError();
	}
	if (glErr2 != GL_NO_ERROR) while(1)Sleep(100);;

	return 0;
}
///////////////////////////////////////////
class Shader
{
public:
	GLuint program_handle;
	Shader(std::string shadername){name=shadername;};
	void attach(int type,char* filename)
	{
		glGetError();
		char* mem=read_file(filename);
		GLuint handle = glCreateShader(type);
		glShaderSource(handle, 1, (const GLchar**)(&mem), 0);
		CHECK_GL_ERROR();
		glCompileShader(handle);
		CHECK_GL_ERROR();

		GLint compileSuccess=0;
		GLchar compilerSpew[256];

		glGetShaderiv(handle, GL_COMPILE_STATUS, &compileSuccess);
		CHECK_GL_ERROR();
		if(!compileSuccess)
		{
			glGetShaderInfoLog(handle, sizeof(compilerSpew), 0, compilerSpew);
			printf("Shader %s\n%s\ncompileSuccess=%d\n",filename,compilerSpew,compileSuccess);
			CHECK_GL_ERROR();
			while(1);;
		}
		handles.push_back(handle);
	}
	void attachfrommemory(int type,char* mem, int size)
	{
		int lunghezza = size;
		glGetError();
		GLuint handle = glCreateShader(type);
		glShaderSource(handle, 1, (const GLchar**)(&mem), &lunghezza);
		CHECK_GL_ERROR();
		glCompileShader(handle);
		CHECK_GL_ERROR();

		GLint compileSuccess=0;
		GLchar compilerSpew[256];

		glGetShaderiv(handle, GL_COMPILE_STATUS, &compileSuccess);
		CHECK_GL_ERROR();
		if(!compileSuccess)
		{
			glGetShaderInfoLog(handle, sizeof(compilerSpew), 0, compilerSpew);
			printf("Shader n%s\ncompileSuccess=%d\n",compilerSpew,compileSuccess);
			CHECK_GL_ERROR();
			while(1);;
		}
		handles.push_back(handle);
	}
	void link()
	{
		glGetError();
		program_handle = glCreateProgram();
		for (int i=0;i<handles.size();i++)
		{
			glAttachShader(program_handle, handles[i]);
			CHECK_GL_ERROR();
		}

		glLinkProgram(program_handle);
		CHECK_GL_ERROR();

		GLint linkSuccess;
		GLchar compilerSpew[256];
		glGetProgramiv(program_handle, GL_LINK_STATUS, &linkSuccess);
		if(!linkSuccess)
		{
			glGetProgramInfoLog(program_handle, sizeof(compilerSpew), 0, compilerSpew);
			printf("Shader Linker:\n%s\nlinkSuccess=%d\n",compilerSpew,linkSuccess);
			CHECK_GL_ERROR();
			while(1);;
		}
		printf("%s linked successful\n",name.c_str());
		CHECK_GL_ERROR();
	}
	void setUniformMatrix4fv(char* varname, GLsizei count, GLboolean transpose, GLfloat *value)
	{
		glGetError();
		GLint loc = glGetUniformLocation(program_handle,varname);
		if (loc==-1) 
		{
			printf("Variable \"%s\" in shader \"%s\" not found\n",varname,name.c_str());
			while(1);;
		};
		glUniformMatrix4fv(loc, count, transpose, value);
		CHECK_GL_ERROR();
	}
	void begin(void)
	{
		glGetError();
		glUseProgram(program_handle);
		CHECK_GL_ERROR();
	}
	void end(void)
	{
		glGetError();
		glUseProgram(0);
		CHECK_GL_ERROR();
	}
private:
	std::vector<GLuint> handles;
	std::string name;

	char* read_file(char* name)
	{
		FILE * fp = fopen (name, "rb");
		
		if (fp==0) 
		{
			printf ("File %s NOT FOUND\n",name);
			while(1);;		
		}
		fseek(fp, 0L, SEEK_END);
		int fsize = ftell(fp);
		fseek(fp, 0L, SEEK_SET);
		char* mem=(char*)malloc(fsize+1);
		for(int i=0;i<fsize+1;i++)mem[i]=0;
		fread (mem, 1, fsize, fp);
		fclose (fp);
		return mem;
	}
};
