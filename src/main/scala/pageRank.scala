import org.apache.spark.sql.{Encoders, SparkSession}

import java.util.ArrayList
import scala.collection.mutable
import scala.collection.mutable.ListBuffer


object pageRank extends App {

  case class Sommet(id: String, pagerank: Double, adjlist: List[String]) {
    /*def Add_adj(page: Sommet): Array[Sommet] = {
      val new_adjlist = adjlist :+ page
      return new_adjlist
    }*/
  }

  var A = Sommet("A", 0.25, List("B", "C"))
  var B = Sommet("B", 0.25, List("C"))
  var C = Sommet("C", 0.25, List("A"))
  var D = Sommet("D", 0.25, List("C"))

  val encoderSchema = Encoders.product[Sommet].schema
  encoderSchema.printTreeString()


  val spark = SparkSession
    .builder()
    .master("local[*]")
    .appName("Spark SQL basic example")
    .config("spark.some.config.option", "some-value")
    .getOrCreate()
  spark.sparkContext.setLogLevel("ERROR")

  import spark.implicits._

  val i = 0
  for (i <- 1 to 20) {
    val rdd = spark.sparkContext.parallelize(List(A, B, C, D))
    val rddCollect = rdd.collect()


    val apresMap = rdd.flatMap(elem => {
      val mapped = new ListBuffer[(String, Double)]()
      var x = ""
      for (x <- elem.adjlist) {
        mapped += ((x, elem.pagerank / elem.adjlist.length))
      }
      mapped.toList

      //(elem.id, elem.pagerank/elem.adjlist.length)
    })
    //apresMap.foreach(println)

    val wordcount = apresMap.reduceByKey(
      (a, b) => {
        a + b
      }
    )

    // (id, (adj, pr))

    var results = wordcount.collect()
    //results.foreach(println(_))

    var mapResults = results.toMap

    A = Sommet("A", mapResults.getOrElse("A", 0.0) * 0.85 + 0.15, List("B", "C"))
    B = Sommet("B", mapResults.getOrElse("B", 0.0) * 0.85 + 0.15, List("C"))
    C = Sommet("C", mapResults.getOrElse("C", 0.0) * 0.85 + 0.15, List("A"))
    D = Sommet("D", mapResults.getOrElse("D", 0.0) * 0.85 + 0.15, List("C"))

  }
  println(List(A, B, C, D))

}