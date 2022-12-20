import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties


def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    element = Beam(doc)
    return element.create(build_ele)


class Beam:
    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):
        self.connect_all_parts(build_ele)
        self.create_lower_part_beam(build_ele)
        return (self.model_ele_list, self.handle_list)

    def connect_all_parts(self, build_ele):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = 3
        com_prop.Stroke = 1
        polyhedron_bottom = self.create_lower_part_beam(build_ele)
        polyhedron_center = self.create_central_part_beam(build_ele)
        polyhedron_top = self.create_top_part_beam(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron_bottom, polyhedron_center)
        if err:
            return
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, polyhedron_top)
        if err:
            return 
        self.model_ele_list.append(
            AllplanBasisElements.ModelElement3D(com_prop, polyhedron))

    # must be updated
    def create_lower_part_beam(self, build_ele):
        polyhedron = self.lower_part_addiction_1(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_2_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_3_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_4_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_2_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_3_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_2_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.lower_part_addiction_3_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.last_lower_part(build_ele))
        return polyhedron

    def create_central_part_beam(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - (build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value), 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                         build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, 
                                         build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value,
                                        build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value,
                                        build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                        build_ele.LengthBottomCut.value, 
                                        build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def create_top_part_beam(self, build_ele):
        polyhedron = self.top_part_addiction_1(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_3(build_ele, plus=(build_ele.Length.value - build_ele.LengthCenterWidth.value)))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_4(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_2_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_4(build_ele, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2, build_ele.WidthTop.value, 10))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_2_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_4_2(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_4_2(build_ele, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2, build_ele.WidthTop.value, 10))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.top_part_addiction_3_3(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.last_top_part(build_ele))
        return polyhedron

    def top_part_addiction_1(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def top_part_addiction_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 , build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 , build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value + 10, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def top_part_addiction_3(self, build_ele, plus=0):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(plus, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(plus, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(plus, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(plus, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(plus, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(plus, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(plus + build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def top_part_addiction_4(self, build_ele, minus_1 = 0, minus_2 = 0, digit = -10):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value + digit - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        print(base_pol)
        print(path)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def top_part_addiction_2_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value, build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value + 10, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def top_part_addiction_2_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def top_part_addiction_4_2(self, build_ele, minus_1 = 0, minus_2 = 0, digit = -10):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - minus_2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - minus_1 + digit, build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def top_part_addiction_3_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def last_top_part(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value + build_ele.HeightPlate.value)
        base_pol += AllplanGeo.Point3D(0, - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 + build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value + build_ele.HeightPlate.value)
        base_pol += AllplanGeo.Point3D(0, - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 + build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base_pol += AllplanGeo.Point3D(0, - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base_pol += AllplanGeo.Point3D(0, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        path += AllplanGeo.Point3D(build_ele.Length.value, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_1(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                    build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 - build_ele.WidthCentralLittle.value,
                                    build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron
    
    def lower_part_addiction_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10 , build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(0, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_4(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def lower_part_addiction_2_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10 ,build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_3_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        path += AllplanGeo.Point3D(build_ele.Length.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_4_2(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def lower_part_addiction_2_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value + 10, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_3_3(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_2_4(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value, build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - 10, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def lower_part_addiction_3_4(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

    def last_lower_part(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0, 20, 0)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - 20, 0)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, 20)
        base_pol += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(0, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base_pol += AllplanGeo.Point3D(0, 0, 20)
        base_pol += AllplanGeo.Point3D(0, 20, 0)

        if not GeometryValidate.is_valid(base_pol):
            return

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 20, 0)
        path += AllplanGeo.Point3D(build_ele.Length.value,20,0)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        
        if err:
            return []

        return polyhedron

