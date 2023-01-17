// Sample effect file

// transformations
float4x4 WorldViewProj : WORLDVIEWPROJECTION;

texture landTex1 < string name = "datas/wired.bmp"; >;

float texSizeX = 769;
float texSizeY = 769;



sampler land1 = sampler_state 
{
    texture = <landTex1>;
    AddressU  = WRAP;        
    AddressV  = WRAP;
    AddressW  = WRAP;
    MIPFILTER = LINEAR;
    MINFILTER = POINT;
    MAGFILTER = POINT;
};



struct VS_COMBINE3
{
    float4 Pos  : POSITION;
    float2 texDetColor : TEXCOORD0;
    float4 diffuse : COLOR0;
};

VS_COMBINE3 CombineVS3( float4 Pos : POSITION, float2 texColor : TEXCOORD0, float4 diffuse : COLOR0)
{
    VS_COMBINE3 output = (VS_COMBINE3)0;
    output.Pos = mul(Pos, WorldViewProj);    // position (view space)    

    output.texDetColor = float2( Pos.x/12, Pos.z/12); 
    output.diffuse = diffuse;

    return output;
}

float4 CombinePS3( VS_COMBINE3 In ) : COLOR0
{
    float4 color = In.diffuse*2*tex2D( land1, In.texDetColor );
    return color;   
}


technique tec
{
    pass p0
    {
        alphablendenable = false;
		//FillMode=WireFrame;
		CullMode = CW;
        VertexShader = compile vs_1_1 CombineVS3();
        PixelShader = compile ps_1_1 CombinePS3();
    }
}



technique FP
{
  pass p0
  {
    MagFilter[0] = POINT;
    MinFilter[0] = POINT;
    MipFilter[0]= POINT;
    lighting = false;
    colorvertex=true;
    EMISSIVEMATERIALSOURCE=color1;
    cullmode=cw;
    texture[0]=<landTex1>;
    ColorArg1[0]=CURRENT;
    ColorArg2[0]=TEXTURE;
    ColorOp[0]=MODULATE;
    
  }
}


