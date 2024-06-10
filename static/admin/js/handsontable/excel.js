var hot,formulaDatas;
var queryFirst,queryPrice,querySoft,queryHard,queryCost,queryBase;
let upValues=[];
var firstVal="物料",priceVal="一箱价格",softVal="软支",hardVal="硬支",costVal="单价",baseVal="基料",opsucess="操作成功",operror="操作失败";;
var btnSave,contextmenu,action;
contextmenu=true;//显示全部右键菜单
//也可使用  ["row_above", "row_below", "undo", "redo"];  设置自定义菜单

//判断是否为空
function isEmpty(s)
{
    if (s == null || s=="undefined" || s.length == 0)
        return true;
    return !/\S/.test(s);
}
//通过特定文字找到单元格
function SearchKey(val)
{
    var search = hot.getPlugin("search");
	return search.query(val);
}

function CheckWuliaoIsAtFirst()
{
	var chk=false,query=queryFirst;
    if(!isEmpty(queryFirst))
    {
	    if(query.length>0)
	    {
		    if(query[0].row==0&&query[0].col==0)
		    {
			    chk=true;
		    }
		    else
		    {
			    alert("第1行第1列必须为[物料]");
			    return false;
		    }
	    }
	    else
	    {
		    alert("第1行第1列必须为[物料]");
		    return false;
	    }
	}
	return chk;
}

function CheckSoftOrHard()
{
    var newSoftVal,newHardVal;
	newSoftVal=querySoft;
	newHardVal=queryHard;
	if(isEmpty(newSoftVal)||isEmpty(newHardVal))
	{
		alert("没有软支或硬支一箱价");
		return false;
	}
	else
	{
		return true;
	}
}
//根据第一列选中的物料ID更新单价
function ChangeSelect(row,value,atOnce)
{
    var newAry=FindAry(value,formulaDatas);
    if(newAry!=-1)
    {
        var query=queryCost;
        var newVal=newAry[1];
        var newVal2=newAry[2];
        if(query.length>0)
        {
            var col=query[0].col;
            if(atOnce)
            {
                hot.setDataAtCell(row,col,newVal);
            }
            else
            {
                upValues.push(new Array(row,col,newVal));
            }
            //更新基料列
            col=queryBase[0].col;
            var celData=hot.getDataAtCell(row,col);
            if(isEmpty(celData))//为空则更新基料列
            {
                if(atOnce)
                {
                    hot.setDataAtCell(row,col,newVal2);
                }
                else
                {
                    upValues.push(new Array(row,col,newVal));
                }
            }
        }
        else
        {
            if(atOnce)
            {
                hot.setDataAtCell(row,1,newVal2);
                hot.setDataAtCell(row,2,newVal);
            }
            else
            {
                upValues.push(new Array(row,1,newVal));
                upValues.push(new Array(row,1,newVal));
            }
        }
    }
}


function UpdatePrice(atOnce)
{
	var firstCol=hot.getDataAtCol(0);
	for(var i=1;i<firstCol.length;i++)
	{
	    var celVal=firstCol[i];
	    if(!isEmpty(celVal))
	    {
	        if(celVal.length>0)
	        {
	            ChangeSelect(i,celVal,atOnce);
	        }
	    }
	}
	if(!atOnce)
	{
        hot.batchRender(() =>
        {
            for(var i=0;i<upValues.length;i++)
            {
                hot.setDataAtCell(upValues[i][0],upValues[i][1],upValues[i][2]);
            }
        });
        upValues.length=0;
    }
}


function FindAry(target,array)
{
    if(!isEmpty(array))
    {
        var i,j;
        for(i=0;i<array.length;i++)
        {
            for(j=0;j<array[0].length;j++)
            {
                if(array[i][j]==target)
                {
                    return array[i];
                }
            }
        }
    }
    return -1;
}

function GetData()
{
	var paraData="action="+action;
	$.ajax({
		type: "POST",
		url: "handler.asp",
		timeout: 10000,
		data:paraData,
        cache:false,
		dataType:"html",
		success:function(res){},
        complete:function(res)
        {
			var result=res.responseText;
			if(result.indexOf("[[")>=0)
			{
				var datas=result.split("$$$"),data1;
				if(isEmpty(datas[0])||datas[0].length<10)//如果是空
				{
				    data1=Handsontable.helper.createSpreadsheetData(32,16);//创建一个32行16列的空表
				}
				else
				{
				    data1=JSON.parse(datas[0]);
				}
				var Columns;
			    if(datas[1].length>2)
			    {
		            Columns=eval("("+datas[1]+")");
		            //Columns=JSON.parse(datas[1]);//因为返回的是嵌套JSON不能使用JSON.parse转换
		        }
			    if(datas[2].length>2)
			    {
		            formulaDatas=JSON.parse(datas[2]);//与第一列联动的名称和单价数组
		        }
				var exceltable = document.getElementById("exceltable");
				hot = new Handsontable(exceltable,{
					data:data1,//表格中的数据项
					colHeaders: true,//当值为true时显示列头，当值为数组时，列头为数组的值
					rowHeaders: true,//当值为true时显示行头，当值为数组时，行头为数组的值
					contextMenu:contextmenu,//右键菜单
					manualColumnResize: true,//调整列大小
					allowInsertRow: true,//允许插入行
					allowInsertColumn: true,//允许插入列
					fillHandle:true,//当值为true时，允许拖动单元格右下角，将其值自动填充到选中的单元格
					search:true,//查询单元格的值 查询单元格的值需要3个步骤：a.设置hot的属性search为true b.创建比对函数 c.渲染比对结果
					columns:Columns,//列设置
                    fixedRowsTop:1,//固定第一行
                    fillHandle:true,//拖动单元格时自动增加新行
                    language:"zh-CN",//中文
                    licenseKey:"6f673-f83c5-43005-a9f45-ecab9",//授权码
					formulas:true,//使用公式
                    afterChange:function(changes,source)
                    {
                        if (source === "edit")
                        {
                            changes.forEach(function (item)
                            {
                                var row = item[0],
                                col = item[1],
                                prevValue = item[2],
                                value = item[3];
                                if(col==0&&prevValue!== value)//改变的是第1列
                                {
                                    ChangeSelect(row,value,true);
                                }
                            });
                        }
                    },
					afterUpdateSettings:function()
					{
				        queryFirst=SearchKey(firstVal);
				        queryPrice=SearchKey(priceVal);
				        querySoft=SearchKey(softVal);
				        queryHard=SearchKey(hardVal);
				        queryCost=SearchKey(costVal);
				        queryBase=SearchKey(baseVal);
	                    UpdatePrice(false);
					}
				});
				if(!hot.isEmptyRow(0))//第一行不为空
				{
			        //设置只读  非编辑基础模板时要设置下
                    hot.updateSettings(
                    {
                        cells:function (row,col,prop)
                        {
                            var cellProperties = {};
                            if(row==0){//0行
                                if(col==0||col==1||col==3)
                                {
			                        cellProperties.readOnly = true;
			                    }
		                    }
		                    else if(row==22&&col==5){
			                    cellProperties.readOnly = true;
		                    }
		                    else if(row==17){
		                        if(col==8||col==9)
		                        {
			                        cellProperties.readOnly = true;
			                    }
		                    }
		                    else if(col==3)
		                    {
		                        cellProperties.readOnly = true;
		                    }
                            //格式化公式
                            var instance=this.instance;
                            var value=instance.getSourceDataAtCell(row,col);//好象不能取到原始公式数据
                            if(!isEmpty(value))
                            {
                                if(value[0]=="=")//公式
                                {
                                    if(isEmpty(cellProperties.className))
                                    {
                                        cellProperties.className = "formula";
                                    }
                                    else
                                    {
                                        cellProperties.className = cellProperties.className+" formula";
                                    }
                                    cellProperties.type="numeric";//必须设置type为numeric才会格式化
                                    cellProperties.numericFormat={pattern:"0.00"};
                                    cellProperties.correctFormat=true;
                                }
                            }
                            return cellProperties;
                        }
                    });
                }
			}
		},
		error: function(e){}
	})
}

function SaveData()
{
	queryFirst=SearchKey(firstVal);
	queryPrice=SearchKey(priceVal);
	querySoft=SearchKey(softVal);
	queryHard=SearchKey(hardVal);
	queryCost=SearchKey(costVal);
	queryBase=SearchKey(baseVal);
	var canSave=false,paraData="action=savedata",alldata;
	canSave=CheckWuliaoIsAtFirst();//判断是否含有某些特殊内容(正式配方表项目中才会使用到)
	if(canSave)
	{
	    canSave=CheckSoftOrHard();//判断是否含有硬支、软支价格(正式配方表项目中才会使用到)
	}
	if(canSave&&(action=="new"||action=="edit"||action=="copy"))
	{
	    canSave=CheckClass();//判断是否选择了所属分类(正式配方表项目中才会使用到)
	    if(canSave)
	    {
	        canSave=CheckInput();//判断是否输入了配方表名称和编码(正式配方表项目中才会使用到)
	    }
	    if(canSave)
	    {
		    alldata=hot.getSourceData();//一定要使用getSourceData不能使用getData，否则公式无法保存
	    }
	}
	else
	{
	    alldata=hot.getSourceData();//一定要使用getSourceData不能使用getData，否则公式无法保存
	    hot.loadData(alldata);
	}
	if(canSave&&!isEmpty(alldata))
	{
		var hotdata=JSON.stringify(alldata);
		var datas=escape(hotdata).replace(/\+/g,"%2B");//将+号转换为%2B
		paraData+="&data="+datas;
		$.ajax({
			type: "POST",
			url: "handler.asp",
			timeout: 10000,
			data:paraData,
			cache:false,
			dataType:"html",
			success:function(res){},
			complete:function(res)
			{
			    var txt=res.responseText.split("$$$");
				if(txt[0]=="1")
				{
				    alert(opsucess);
				}
				else
				{
					alert(txt[1]);
				}
			},
			error:function(e){}
		});
	}
}

function btnClick()
{
    SaveData();
}

$(document).ready(function()
{
    action="";
	GetData();
	btnSave=document.getElementById("btnSave");
	Handsontable.dom.addEvent(btnSave,"click",function()
	{
		SaveData();
	});
});