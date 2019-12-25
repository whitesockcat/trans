import xml.dom.minidom
import os
import xml.etree.ElementTree as ET

############################################
# xml_folder = 'xml/'
# wh = (0,0)
############################################


def obj_to_det_xml(obj_list,
                   xml_path,
                   satellite_name='CCD',
                   sensor_name='CCD',
                   imaging_time='2019',
                   resolution=0.5,
                   target_name="none", target_id='none',
                   ):
    """ 将结果存储到指定xml
    :param obj_list: 检测识别结果
    :param xml_path: xml存储路径
    :return: 无
    """
    obj_n = len(obj_list)
    if obj_n == 0:
        return 0
    doc = xml.dom.minidom.Document()
    root_node = doc.createElement("ImageInfo")
    root_node.setAttribute("satellite", satellite_name)
    root_node.setAttribute("sensor", sensor_name)
    root_node.setAttribute("imagingtime", imaging_time)
    root_node.setAttribute("resolution", "%.2f" % float(resolution))
    doc.appendChild(root_node)

    BaseInfo_node = doc.createElement("BaseInfo")
    BaseInfo_node.setAttribute("name", target_name)
    BaseInfo_node.setAttribute("ID", target_id)
    BaseInfo_node.setAttribute("description", "target detection result")
    root_node.appendChild(BaseInfo_node)

    result_node = doc.createElement("result")
    DetectNumber_node = doc.createElement("DetectNumber")
    DetectNumber_value = doc.createTextNode(str(obj_n))
    DetectNumber_node.appendChild(DetectNumber_value)
    result_node.appendChild(DetectNumber_node)

    for ii in range(obj_n):
        obj = obj_list[ii]
        DetectResult_node = doc.createElement("DetectResult")

        ResultID_node = doc.createElement("ResultID")
        ResultID_value = doc.createTextNode(str(ii))
        ResultID_node.appendChild(ResultID_value)

        Shape_node = doc.createElement("Shape")

        obj_points = obj['xy']

        for xy in obj_points:
            x, y = xy
            Point_node = doc.createElement("Point")
            Point_value = doc.createTextNode("%.6f, %.6f" % (x, y))
            Point_node.appendChild(Point_value)
            Shape_node.appendChild(Point_node)

        Location_node = doc.createElement("Location")
        Location_value = doc.createTextNode("unknown")
        Location_node.appendChild(Location_value)

        CenterLonLat_node = doc.createElement("CenterLonLat")
        CenterLonLat_value = doc.createTextNode("0.000000, 0.000000")
        CenterLonLat_node.appendChild(CenterLonLat_value)

        Length_node = doc.createElement("Length")
        Length_value = doc.createTextNode("0")
        Length_node.appendChild(Length_value)

        Width_node = doc.createElement("Width")
        Width_value = doc.createTextNode("0")
        Width_node.appendChild(Width_value)

        Area_node = doc.createElement("Area")
        Area_value = doc.createTextNode("0")
        Area_node.appendChild(Area_value)

        Angle_node = doc.createElement("Angle")
        Angle_value = doc.createTextNode("0")
        Angle_node.appendChild(Angle_value)

        Probability_node = doc.createElement("Probability")
        Probability_value = doc.createTextNode("1.0")
        Probability_node.appendChild(Probability_value)

        ResultImagePath_node = doc.createElement("ResultImagePath")
        ResultImagePath_value = doc.createTextNode(" ")
        ResultImagePath_node.appendChild(ResultImagePath_value)

        ValidationName_node = doc.createElement("ValidationName")
        ValidationName_value = doc.createTextNode(" ")
        ValidationName_node.appendChild(ValidationName_value)

        cat = obj['cat']
        p = obj['p']

        PossibleResults_node = doc.createElement("PossibleResults")

        Type_node = doc.createElement("Type")
        # Type_value = doc.createTextNode("%s" % weapon.name)
        Type_value = doc.createTextNode(cat)
        Type_node.appendChild(Type_value)

        Reliability_node = doc.createElement("Reliability")
        Reliability_value = doc.createTextNode("%.3f" % p)
        Reliability_node.appendChild(Reliability_value)

        PossibleResults_node.appendChild(Type_node)
        PossibleResults_node.appendChild(Reliability_node)
        DetectResult_node.appendChild(PossibleResults_node)

        DetectResult_node.appendChild(ResultID_node)
        DetectResult_node.appendChild(Shape_node)
        DetectResult_node.appendChild(Location_node)
        DetectResult_node.appendChild(CenterLonLat_node)
        DetectResult_node.appendChild(Length_node)
        DetectResult_node.appendChild(Width_node)
        DetectResult_node.appendChild(Area_node)
        DetectResult_node.appendChild(Angle_node)
        DetectResult_node.appendChild(Probability_node)
        DetectResult_node.appendChild(ResultImagePath_node)
        DetectResult_node.appendChild(ValidationName_node)

        result_node.appendChild(DetectResult_node)
    root_node.appendChild(result_node)
    print('xml_path', xml_path)
    with open(xml_path, "wb+") as f:
        f.write(doc.toprettyxml(indent="\t", newl="\n", encoding="utf-8"))

    # print('success write ', xml_path)
    return 0


def get_xy_from_shape(shape, num, offset):
    offset_x, offset_y = offset
    xy = shape.findall('Point')[num].text
    x,y = float(xy.split(',')[0]) + offset_x, float(xy.split(',')[1]) + offset_y
    return x,y

def get_offset(name, wh):
    w, h = wh
    part_num = name.split('_')[-1].split('.')[0]
    if part_num == '0':
        offset = (0,0)
    elif part_num == '1':
        offset = (int(w/2),0)
    elif part_num == '2':
        offset = (int(w/2),int(h/2))
    elif part_num == '3':
        offset = (0,int(h/2))
    return offset

def four2one(xml_folder, wh):
    '''
    用全图尺寸计算小图响应的经纬度坐标
    wh = (w, h)
    '''
    xml_files = os.listdir(xml_folder)
    det_result = []
    for xml_file in xml_files:
        xml_path = xml_folder + xml_file
        tree = ET.ElementTree(file=xml_path)

        root = tree.getroot()

        offset = get_offset(xml_path, wh)
        num=int(root[1].findall('DetectNumber')[0].text)
        # print('det num', num)
        # det_num += num
        result=root[1].findall('DetectResult')
        assert len(result) == num
        result_sliding = {}
        for i in range(num):
            cat_and_p = result[i].findall('PossibleResults')[0]
            cat = cat_and_p.findall('Type')[0].text
            p = float(cat_and_p.findall('Reliability')[0].text)
            shape = result[i].findall('Shape')[0]
            result_sliding['cat'] = cat
            result_sliding['p'] = p
            result_sliding['xy'] = [get_xy_from_shape(shape, i, offset) for i in range(5)]
            print(result_sliding['xy'])
            det_result.append(result_sliding)

    # det['det_num'] = det_num
    # det['det_result'] = det_result
    # print(det_result)
    # print(det_num)
    obj_to_det_xml(det_result, 'test.xml')